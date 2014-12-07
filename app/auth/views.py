import json
import urllib2
from urlparse import urlparse
import re # REGEX

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
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
from app.messages import *
from app.helpers import *
from app.auth.specific_login import get_university


@require_POST
def login_action(request):
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
                messages.error(request, UNIV_CONNECTEDED_NO_EMAIL, extra_tags="hidden")
                return redirect( reverse('welcome') )
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
                if 'photourl' in user_details:
                    photo_url = user_details['photourl']
                    photo_ext = urlparse(photo_url).path.split('/')[-1].split('.')[-1]
                    photo_name = login_user + "." + photo_ext

                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(urllib2.urlopen(photo_url).read())
                    img_temp.flush()

                    user.profile_picture.save(photo_name, File(img_temp), save=False)
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
            messages.error(request, WRONG_USERNAME_OR_PASSWORD, extra_tags="hidden")
            return redirect( reverse('welcome') )

    login(request, user)
    if new_user:
        return redirect( reverse('explore') )
    return redirect( reverse('dashboard') )


@require_POST
def signup_action(request):

    form = SignupForm(request.POST)
    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_SIGNUP_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect( reverse('welcome') )

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
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
        user = jUser.objects.get_object_or_404(email = email)
        user.set_password(password)
        # If they have chosen a different username, let them keep it if it is free
        if username != user.username:
            user.username = username
        user.is_active = False
        user.is_fake = False
        user.save()
    else:
        # No user with the same email exists (no fake account)
        user = jUser.objects.create_user(username=username, user_type=user_type,
                                    password=password, email=email, university=university,
                                    first_name=fname, last_name=lname)
        user.is_active = False
        user.save()

    # Authenticate user
    auth_user = authenticate(username=user.username, password=password)
    if auth_user is not None:
        login(request, auth_user)
        send_email_confirmation(request, request.user)

    return redirect('/')


@login_required
def logout_action(request):
    logout(request)
    return redirect('/')


@require_GET
@login_required
def resend_confirmation_email(request):
    user = request.user
    if not user.email:
        redirect( reverse('set_email') )

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
        return redirect( reverse("home") )

    if request.method == "GET":
        return render(request, "pages/auth/set_email.html", context)

    form = EmailConfirmationForm(request.POST)
    if not form.is_valid():
        messages.error(request, form.non_field_errors)
        return redirect( reverse('set_email') )

    email = form.cleaned_data["email"]
    university = form.cleaned_data["university"]

    user.university = university
    user.email = email
    user.save()

    send_email_confirmation(request, user)
    return redirect( reverse("home") )


def validate_user(request, username, confirmation):
    # Validate users email based on username and confirmation hash
    users = jUser.objects.filter(username=username)
    if not users:
        return token_failed(request)
    user = users[0]

    if user.is_active:
        return redirect( reverse('home') )

    if not default_token_generator.check_token(user, confirmation):
        return token_failed(request)

    user.is_active = True
    user.save()

    return redirect( reverse('home') )


def delete_user(request, username, confirmation):
    # If a user receives a confirmation e-mail, but they didn't sign up,
    # they can delete their account by following the delete link.
    message = render_to_string("objects/notifications/auth/user_deleted.html", {})

    users = jUser.objects.filter(username=username)
    if not users:
        messages.success(request, message)
        return redirect( reverse("welcome") )

    user = users[0]
    if not default_token_generator.check_token(user, confirmation):
        return token_failed(request)

    logout(request)
    user.delete()

    messages.success(request, message)
    return redirect( reverse("welcome") )


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
    dict_error = {
        "status": "Error"
    }

    if len(email) == 0:
        dict_error["message"] = "E-mail cannot be empty"
        return HttpResponse(json.dumps(dict_error))


    if jUser.objects.filter(email=email, is_fake = False).count() > 0:
        dict_error["message"] = "E-mail address exists"
        return HttpResponse(json.dumps(dict_error))

    try:
        _, domain = email.split("@")
    except ValueError as e:
        dict_error["message"] = "Not a valid e-mail address"
        return HttpResponse(json.dumps(dict_error))

    universities = University.objects.filter(domains__name=domain)

    if not universities:
        dict_error["message"] = "University not found"
        return HttpResponse(json.dumps(dict_error))
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
    username_regex = re.compile("^[A-Za-z0-9\._-]{3,25}$")
    username = request.GET["username"]
    dict_error = {
        "status": "Error"
    }

    if username == "":
        dict_error["message"] = "Username is required"
        return HttpResponse(json.dumps(dict_error))
    elif not username_regex.match(username):
        dict_error["message"] = "Username can only contain alphanumeric characters, underscores, hyphens or dots."
        if len(username) < 3:
            dict_error['message'] = "Username cannot have less than 3 characters."
        elif len(username) > 25:
            dict_error['message'] = "Username cannot have more thatn 25 characters."
        return HttpResponse(json.dumps(dict_error))
    elif jUser.objects.filter(username=username, is_fake = False).count() > 0:
        dict_error["message"] = "Username exists"
        return HttpResponse(json.dumps(dict_error))
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
    username_regex = re.compile("^[A-Za-z0-9\._-]{3,25}$")
    dict_error = {
        "status": "Error"
    }

    try:
        _, domain = email.split('@')
    except ValueError:
        dict_error["message"] = "Not a valid e-mail address"
        return HttpResponse(json.dumps(dict_error))
    if jUser.objects.filter(email=email, is_fake=False).count() > 0:
        dict_error["message"] = "E-mail address exists"
        return HttpResponse(json.dumps(dict_error))
    elif not username_regex.match(username):
        dict_error["message"] = "Username not valid."
        return HttpResponse(json.dumps(dict_error))
    elif jUser.objects.filter(username=username, is_fake = False).count() > 0:
        dict_error["message"] = "Username exists."
        return HttpResponse(json.dumps(dict_error))
    elif University.objects.filter(domains__name=domain).count() == 0:
        dict_error["message"] = "University not found"
        return HttpResponse(json.dumps(dict_error))

    return_dict = {
        "status": "OK",
    }
    return HttpResponse(json.dumps(return_dict))


@require_POST
def send_email_pw_reset(request):
    form = EmailPasswordResetForm(request.POST)

    if not form.is_valid():
        messages.error(request, "There is no such user registered with that email.")
        return redirect( reverse('welcome') )

    user = form.cleaned_data['user']
    token = default_token_generator.make_token(user)
    password_reset_link = request.build_absolute_uri( reverse('password_reset', args=(user.username, token)) )
    
    email_context = {
        "fname": user.first_name,
        "password_reset_link": password_reset_link
    }
    email_body = render_to_string("emails/reset_password.html", email_context)

    send_mail("Reset your password on connect.academy", email_body, "noreply@connect.academy", [user.email], fail_silently=False)

    success_message = render_to_string("objects/notifications/auth/pw_reset_email_sent.html", {})
    messages.success(request, success_message)
    return redirect( reverse('welcome') )


def password_reset(request, username, token):
    context = {
        "page": "manage_account",
        "reset_password": True,
        "page_id": "reset_password"
    }

    user = get_object_or_404(jUser, username=username)
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Fake the call to authenticate() by setting the backend attribute
    user.backend = "app.auth.helpers.jUserBackend"
    login(request,user)

    return render(request, "pages/auth/manage_account.html", context)

def new_password(request):
    context = {
        "page": "manage_account",
    }

    user = request.user
    form = NewPasswordForm(request.POST)

    if not form.is_valid():
        context["reset_password"] = True
        context["page_id"] = "reset_password"
        context["error"] = form.non_field_errors
        return render(request, "pages/auth/manage_account.html", context)
    
    user.set_password(form.cleaned_data['new_pass'])
    user.save()

    context["success"] = "Your password has been changed successfully"

    return render(request, "pages/auth/manage_account.html", context)