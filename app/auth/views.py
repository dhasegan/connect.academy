from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.defaults import server_error
from django.db import IntegrityError

from app.models import *
from app.course_info import *
from app.context_processors import *
from app.helpers import *
from app.auth.forms import *
from app.auth.specific_login import get_university


@require_POST
def login_action(request):
    context = {}

    form = LoginForm(request.POST)
    if not form.is_valid():
        raise Http404

    # login_user is the username OR email of the user attempting login.
    login_user = form.cleaned_data['username']
    login_pass = form.cleaned_data['password']

    # Using jUserBackend, which also tries to find a match for the email address.
    user = authenticate(username=login_user, password=login_pass)
    if user is None:
        auth_univ = get_university(login_user, login_pass)
        if auth_univ:
            users = jUser.objects.filter(username=login_user)
            if not users:
                universities = University.objects.filter(domains__name=auth_univ["domain"])
                if not universities:
                    raise IntegrityError
                university = universities[0]

                user = jUser.objects.create_user(username=login_user, password=login_pass, university=university)
                user.is_active = False  # Account inactive until confirmed
                user.save()

            user = authenticate(username=login_user, password=login_pass)

        if not auth_univ or user is None:
            # user not found neither on our database nor on campusnet
            context['error'] = render_to_string("objects/notifications/auth/wrong_username_or_password.html", {})
            return render(request, "pages/welcome_page.html", context)

    login(request, user)
    return redirect("/home")


@login_required
def logout_action(request):

    logout(request)
    return redirect('/')


@require_GET
@login_required
def resend_confirmation_email(request):
    user = request.user
    if not user.email:
        raise Http404

    send_email_confirmation(request, user)
    return HttpResponse()


@require_http_methods(["POST", "GET"])
@login_required
def set_email(request):
    context = {
        "page": "set_email",
    }
    user = request.user

    if user.email:
        return redirect("/home")

    if request.method == "GET":
        return render(request, "pages/set_email.html", context)

    form = EmailConfirmationForm(request.POST)
    if not form.is_valid():
        context['error'] = form.non_field_errors
        return render(request, "pages/set_email.html", context)

    email = form.cleaned_data["email"]
    university = form.cleaned_data["university"]

    user.university = university
    user.email = email
    user.save()

    send_email_confirmation(request, user)
    return redirect("/home")


def validate_user(request, username, confirmation):
    # Validate user based on username and confirmation hash
    user = get_object_or_404(jUser, username=username)

    if not default_token_generator.check_token(user, confirmation):
        raise Http404

    user.is_active = True
    user.save()

    return redirect("/")


def delete_user(request, username, confirmation):
    # If a user receives a confirmation e-mail, but they didn't sign up, they can delete their account by following
    # the delete link.
    context = {
        "page": "delete"
    }
    user = get_object_or_404(jUser, username=username)
    if not default_token_generator.check_token(user, confirmation):
        raise Http404

    user.delete()
    context["success"] = "User successfully deleted. <br/>"
    return render(request, "pages/welcome_page.html", context)


@require_POST
def signup_action(request):
    context = context = {
        "page": "signup_action",
    }
    context.update(csrf(request))

    form = SignupForm(request.POST)
    if not form.is_valid():
        raise Http404

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
    password_confirmation = form.cleaned_data["password_confirmation"]
    email = form.cleaned_data["email"]
    fname = form.cleaned_data["fname"]
    lname = form.cleaned_data["lname"]
    is_instructor = form.cleaned_data["is_instructor"]
    department_id = form.cleaned_data["department"]
    emailID, domain = email.split("@")

    if is_instructor:
        user_type = USER_TYPE_INSTRUCTOR
    else:
        user_type = USER_TYPE_STUDENT

    # Check if username or email exists
    users_same_name = jUser.objects.filter(username=username).count()
    users_same_email = jUser.objects.filter(email=email).count()
    error = False  # No error
    if users_same_name > 0:
        context["error"] = "Sorry, that <b>username</b> is taken. Please try a different one. <br/>"
        error = True
    if users_same_email > 0:
        if "error" in context:
            context["error"] += "A user with that <b>e-mail address</b> already exists. If you already have an account, you can log in on the panel above.<br/>"
        else:
            context["error"] = "A user with that <b>e-mail address</b> already exists. If you already have an account, you can log in on the panel above.<br/>"

    if "error" in context:
        return render(request, "pages/welcome_page.html", context)

    # Check if we know the domain of the e-mail address
    universities = University.objects.filter(domains__name=domain)
    if len(universities) < 1:  # not found
        context["error"] = "Sorry, we don't have a <b>university</b> with the domain of your <b>e-mail address</b>. Please check again soon.<br/>"
        return render(request, "pages/welcome_page.html", context)

    # university found
    university = universities[0]

    # create user
    if (password_confirmation == password):  # passwords match

        user = jUser.objects.create_user(username=username, user_type=user_type, password=password, email=email, university=university,
                                         first_name=fname, last_name=lname)

        if department_id:
            department = Department.objects.filter(id=department_id)[0]
            if department and len(department.name) > 0:
                department.save()
                user.departments.add(department)

        user.is_active = False

        # save new user
        user.save()

        # Authenticate user
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            login(request, auth_user)
            # it needs to be request.user, not auth_user.
            send_email_confirmation(request, request.user)
            if 'login' in request.META.get('HTTP_REFERER'):
                return redirect('/')
            return redirect(request.META.get('HTTP_REFERER'))
    else:  # passwords don't match
        if "error" in context:
            context["error"] += "Your <b>passwords</b> don't match. Please try again. <br/>"
        else:
            context["error"] = "Your <b>passwords</b> don't match. Please try again. <br/>"
            return render(request, "pages/welcome_page.html", context)
