from django.template.loader import render_to_string
from django.conf import settings

from app.models import *
from app.ratings import *


def debug(context):
    return {
        'DEBUG': settings.DEBUG
    }


def user_authenticated(request):
    context = {}
    if request.user and request.user.is_authenticated():
        user = request.user
        context["user_auth"] = user
        if not user.is_active:
            if not user.email or user.email == "":
                context['warning'] = render_to_string('objects/notifications/auth/email_not_set.html', {})
            else:
                context['warning'] = render_to_string('objects/notifications/auth/email_not_activated.html', {})

    return context
