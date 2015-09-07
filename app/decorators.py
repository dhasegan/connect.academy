from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse

from app.models import *
from app.decider import decider

def require_student(view):
    def decorated(request, *args, **kwargs):
        if request.user is None or request.user.juser.user_type != USER_TYPE_ADMIN:
            raise Http404
        return view(request, *args, **kwargs)
    return decorated

def require_professor(view):
    def decorated(request, *args, **kwargs):
        if request.user is None or request.user.juser.user_type != USER_TYPE_PROFESSOR:
            raise Http404
        return view(request, *args, **kwargs)
    return decorated

def require_admin(view):
    def decorated(request, *args, **kwargs):
        if request.user is None or request.user.juser.user_type != USER_TYPE_ADMIN:
            raise Http404
        return view(request,*args, **kwargs)
    return decorated

# Active juser
def require_active_user(view):
    def decorated(request, *args, **kwargs):
        if not request.user:
            raise Http404
        juser = get_object_or_404(jUser, id=request.user.id)
        if not juser.is_active:
            messages.error(request, "Please activate your account to be able to post to connect.")
            return redirect(reverse('home'))
        return view(request,*args, **kwargs)
    return decorated

# Require a specific feature to be turned on for this user
def require_decider(feature_name):
    def requiure_decider_decorator(view):
        def decorated(request, *args, **kwargs):
            decider.fail_on_unavailable(request, feature_name)
            return view(request,*args, **kwargs)
        return decorated
    return requiure_decider_decorator

# This decorator takes a list of USER_TYPE ints and raises Http404 if the logged in user
# is not of any type mentioned in the list
# example usage:

# @require_user_type([USER_TYPE_PROFESSOR, USER_TYPE_ADMIN])
# def view(request):
#   #view body
def require_user_type(type_list):
    def check_type(view):
        def decorated(request, *args, **kwargs):
            user = request.user.juser
            if user is None or not user.user_type in type_list:
                raise Http404
            return view(request, *args, **kwargs)
        return decorated
    return check_type
