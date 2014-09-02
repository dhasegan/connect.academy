import json
import urllib2
from urlparse import urlparse

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.defaults import server_error
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.conf import settings

from app.models import *
from app.auth.forms import *
from app.auth.helpers import *
from app.decorators import *
from app.auth.specific_login import get_university

@require_POST
def login_action(request):
    context = {}

    form = LoginForm(request.POST)
    if not form.is_valid():
        raise Http404

    # login_user is the username OR email of the user attempting login.
    login_user = form.cleaned_data['user_auth']
    login_pass = form.cleaned_data['password']
    new_user = False

    # Using jUserBackend, which also tries to find a match for the email address.
    user = authenticate(username=login_user, password=login_pass)
    if user is None:
        auth_univ = get_university(login_user, login_pass)
        if auth_univ:
            # CN success
            if not login_user in settings.JACOBS_USER_DETAILS:
                context['error'] = render_to_string("objects/notifications/auth/CN_connected_but_no_email.html", {})
                return render(request, "pages/welcome_page.html", context)
            users = jUser.objects.filter(username=login_user)
            if not users:
                university = University.objects.get(name=auth_univ["name"])
                user_details = settings.JACOBS_USER_DETAILS[login_user]
                user = jUser.objects.create_user(username=login_user, password=login_pass, university=university, email=user_details['email'], \
                                                 first_name=user_details['first_name'], last_name=user_details['last_name'], 
                                                 user_type=USER_TYPE_STUDENT)
                user.is_active = True
                if 'description' in user_details:
                    user.summary = user_details['description']
                # if 'photourl' in user_details:
                #     photo_url = user_details['photourl']
                #     photo_ext = urlparse(photo_url).path.split('/')[-1].split('.')[-1]
                #     photo_name = login_user + "." + photo_ext

                #     img_temp = NamedTemporaryFile(delete=True)
                #     img_temp.write(urllib2.urlopen(photo_url).read())
                #     img_temp.flush()

                #      user.profile_picture.save(photo_name, File(img_temp), save=False)
                user.save()
                send_email_confirmation(request, user)
                new_user = True
            else:
                user = users[0]
                user.set_password(login_pass)
                user.is_fake = False
                user.save()

            user = authenticate(username=login_user, password=login_pass)

        if not auth_univ or user is None:
            # User not found neither on our database nor on campusnet
            context['error'] = render_to_string("objects/notifications/auth/wrong_username_or_password.html", {})
            context['page'] = "welcome"
            return render(request, "pages/welcome_page.html", context)

    login(request, user)
    if new_user:
        return redirect( reverse('explore') )
    return redirect( reverse('dashboard') )


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
        return render(request, "pages/auth/set_email.html", context)

    form = EmailConfirmationForm(request.POST)
    if not form.is_valid():
        context['error'] = form.non_field_errors
        return render(request, "pages/auth/set_email.html", context)

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
        context['error'] = form.non_field_errors
        return render(request, "pages/welcome_page.html", context)

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
    password_confirmation = form.cleaned_data["password_confirmation"]
    email = form.cleaned_data["email"]
    fname = form.cleaned_data["fname"]
    lname = form.cleaned_data["lname"]
    is_professor = form.cleaned_data["is_professor"]
    is_alumnus = form.cleaned_data['is_alumnus']
    has_fake_account = form.cleaned_data['has_fake_account']
    university = form.cleaned_data["university"]

    if is_alumnus:
        user_type = USER_TYPE_ALUMNUS
    elif is_professor:
        user_type = USER_TYPE_PROFESSOR
    else:
        user_type = USER_TYPE_STUDENT

    if has_fake_account:
        user = jUser.objects.get(email = email)
        print user.username
        user.set_password(password)
        # If they have chosen a different username, let them keep it if it is free
        if username != user.username and jUser.objects.filter(username=username).count() == 0:
            user.username = username
        user.is_active = False
        user.is_fake = False
        user.save()
    else:
        user = jUser.objects.create_user(username=user.username, user_type=user_type, password=password, email=email, university=university,
                                     first_name=fname, last_name=lname, is_active = False)
    
        user.save()
    # Authenticate user
    print 
    auth_user = authenticate(username=user.username, password=password)
    if auth_user is not None:
        login(request, auth_user)
        send_email_confirmation(request, request.user)

    return redirect('/')


@require_GET
def university_by_email(request):
# This function handles the asynchronous get requests sent by the javascript code,
# during user registration to confirm that the e-mail address (in the GET parameters)
# is available and valid.
# It returns a HTTP response with:
#   The name of the university (taken by the domain of the e-mail address) if it is found
#   "Exists" if a user with that e-mail address already exists
#   "NotFound" if a university with that domain is not found

    email = request.GET["email"]

    if len(email) == 0:
        return_dict = {
            "status": "Error",
            "message": "E-mail cannot be empty"
        }
        return HttpResponse(json.dumps(return_dict))


    if jUser.objects.filter(email=email, is_fake = False).count() > 0:
        return_dict = {
            "status": "Error",
            "message": "E-mail address exists"
        }
        return HttpResponse(json.dumps(return_dict))

    try:
        _, domain = email.split("@")
    except ValueError as e:
        return_dict = {
            "status": "Error",
            "message": "Not a valid e-mail address"
        }
        return HttpResponse(json.dumps(return_dict))

    universities = University.objects.filter(domains__name=domain)

    if not universities:
        return_dict = {
            "status": "Error",
            "message": "University not found"
        }
        return HttpResponse(json.dumps(return_dict))
    else:
        university = universities[0]
        return_dict = {
            "status": "OK",
            "message": university.name
        }
        return HttpResponse(json.dumps(return_dict))


@require_GET
def check_username(request):
# This function handles the asynchronous get requests sent by the javascript code,
# to check if the username (from the registration form) is valid
# It returns:
#   "Username is required" if the username is empty
#   "Username exists" if a user with that username exists
#   "OK" if the username is available
    username = request.GET["username"]
    if username == "":
        return_dict = {
            "status": "Error",
            "message": "Username is required"
        }
        return HttpResponse(json.dumps(return_dict))
    if jUser.objects.filter(username=username, is_fake = False).count() > 0:
        return_dict = {
            "status": "Error",
            "message": "Username exists"
        }
        return HttpResponse(json.dumps(return_dict))
    else:
        return_dict = {
            "status": "OK",
            "message": "Username OK"
        }
        return HttpResponse(json.dumps(return_dict))


@require_GET
def validate_registration(request):
# This function handles the asynchronous get requests sent by the javascript code,
# to validate the username and the e-mail address on form submission
# It returns:
#   "Error" if the username or e-mail address are not valid
#   "OK" if they are both valid.
    username = request.GET['username']
    email = request.GET['email']

    try:
        _, domain = email.split('@')
    except ValueError:
        return_dict = {
            "status": "Error",
            "message": "Not a valid e-mail address"
        }
        return HttpResponse(json.dumps(return_dict))

    if jUser.objects.filter(email=email, is_fake=False).count() > 0:
        return_dict = {
            "status": "Error",
            "message": "E-mail address exists"
        }
        return HttpResponse(json.dumps(return_dict))
    elif jUser.objects.filter(username=username, is_fake = False).count() > 0:
        return_dict = {
            "status": "Error",
            "message": "Username exists."
        }
        return HttpResponse(json.dumps(return_dict))
    elif University.objects.filter(domains__name=domain).count() == 0:
        return_dict = {
            "status": "Error",
            "message": "University not found"
        }
        return HttpResponse(json.dumps(return_dict))
    else:
        return_dict = {
            "status": "OK",
        }
        return HttpResponse(json.dumps(return_dict))


@require_POST
@require_active_user
@login_required
def approve_student_registrations(request):
    context = {
        'page': 'approve_student_registrations',
    }
    context.update(csrf(request))

    # Make sure the logged in user is allowed to approve these registrations
    user = request.user
    course_id = request.POST['course']
    courses = Course.objects.filter(id=course_id)
    if courses is None:
        raise Http404
    else:
        course = courses[0]
    registrations = ProfessorCourseRegistration.objects.filter(course=course, professor=user, is_approved=True)
    if registrations is None:
        raise Http404

    # At this point we know that an approved professor of the course
    # is attempting to approve sudent registrations

    # Approve each registration
    for key, val in request.POST.items():
        if 'student' in key:
            _, student_id = key.split('-')
            registrations = StudentCourseRegistration.objects.filter(course_id=course_id,
                                                                     student_id=student_id,
                                                                     is_approved=False)
            if registrations is not None:
                registration = registrations[0]
            else:
                raise Http404

            # Approve registration
            if val:
                registration.is_approved = True
                registration.save()

    get_params = "?page=teacher"
    return redirect( reverse('course_page', args=(course.slug,)) + get_params )
