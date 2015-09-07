import json

from django.conf import settings
from django.core.exceptions import PermissionDenied

def is_available(decider_name, username = None):
    if decider_name in settings.DECIDERS_VALUES:
        decider = settings.DECIDERS_VALUES[decider_name]
        return decider['available'] or username in decider.get('users', [])
    return False

def fail_on_unavailable(request, decider_name):
    username = None
    if request.user and request.user.is_authenticated():
        username = request.user.username
    if not is_available(decider_name, username):
        raise PermissionDenied

def available_deciders(username = None):
    activated_features = []
    for decider_name in settings.DECIDERS_VALUES.iterkeys():
        if is_available(decider_name, username):
            activated_features.append(decider_name)
    return activated_features
