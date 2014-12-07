from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse

from app.models import *


def send_email_confirmation(request, user):

    fname = user.first_name
    if not fname:
        fname = user.username
    confirmation_hash = default_token_generator.make_token(user)
    confirmation_link = request.build_absolute_uri( reverse('confirmation', args=(user.username, confirmation_hash)) )
    delete_link = request.build_absolute_uri( reverse('delete', args=(user.username, confirmation_hash)) )

    context = {
        'fname': fname,
        'confirmation_link': confirmation_link,
        'delete_link': delete_link
    }
    message = render_to_string("emails/require_confirmation.html", context)

    send_mail("Connect.Academy Account Confirmation", message, "noreply@connect.academy", [user.email], fail_silently=False)

def token_failed(request):
    error_message = render_to_string("objects/notifications/auth/token_failed.html", {})
    messages.error(request, error_message)
    if request.user.is_authenticated:
        return redirect( reverse("home") )
    else:
        return redirect( reverse("welcome") )

# Serialize the form errors to prepare them to be sent as message
def serialize_form_errors(request, form, prefix):
    field = {
        "email": "Your email",
        "username": "A username",
        "fname": "Your first name",
        "lname": "Your last name",
        "password": "A password",
        "password_confirmation": "Confirmation of the password"
    }
    field_errors = []
    for e in form.errors.keys():
        if e in field:
            field_errors.append(field[e] + " is required. Please enter it below!")
    errors = "<!>".join([e for e in field_errors + form.non_field_errors()])
    return prefix + errors

class jUserBackend(object):

    def authenticate(self, username=None, password=None):
        try:
            user = jUser.objects.get(Q(email=username) | Q(username=username))
            if user.check_password(password):
                return user
        except jUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return jUser.objects.get(pk=user_id)
        except jUser.DoesNotExist:
            return None
