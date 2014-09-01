from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.template.loader import render_to_string

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

    send_mail("Connect.Academy Account Confirmation", message, "Connect.Academy <noreply@connect.academy>", [user.email], fail_silently=False)


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
