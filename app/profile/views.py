# Shortcuts
from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string
from app.helpers import *
import hashlib
import string
import random

# Mimetypes for images
from mimetypes import guess_type

# App Models
from app.models import *
from app.course_info import *
from app.context_processors import *
from app.profile.forms import *
from app.campusnet_login import *

@require_GET
@login_required
def profile(request,username):
    # stub for profile view
    context = {'page': 'profile'}
    user = jUser.objects.filter(username=username)
    if user:
        user = user[0] 
        context['user'] = user

    return render(request,"pages/profile.html",context)

@require_GET
@login_required
def manage_account(request):
    context = {
        'page': 'manage_account'
    }
    return render(request,"pages/user_account.html",context)

@require_POST
@login_required
def password_change_action(request):
    context = {
        'page': 'manage_account'
    }
    context.update(csrf(request))

    form = ChangePasswordForm(request.POST)
    
    if not form.is_valid():
        raise Http404

    old_password = form.cleaned_data['old_pass']
    new_password = form.cleaned_data['new_pass']
    confirm_pass = form.cleaned_data['confirm_new_pass']

    user = request.user
    user = authenticate(username = user.username, password = old_password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(request,"pages/user_account.html",context)

    if new_password != confirm_pass:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_passwords.html', {})
        return render(request,"pages/user_account.html",context)

    #everything went fine

    user.set_password(new_password)
    user.save()
    context['success'] = render_to_string('objects/notifications/profile/changed_object.html',{ 'changed_object': "password" })

    return render(request,"pages/user_account.html",context)

@require_POST
@login_required
def username_change_action(request):
    context = {
        'page': 'manage_account'
    }

    form = ChangeUsernameForm(request.POST)

    if not form.is_valid():
        raise Http404

    new_username = form.cleaned_data['new_username']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username=user.username, password = password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(request,"pages/user_account.html",context)

    #proceed and change the username.

    user.username = new_username
    user.save()

    context['success'] = render_to_string('objects/notifications/profile/changed_object.html',{ 'changed_object': "username" })

    return render(request,"pages/user_account.html",context)

@require_POST
@login_required
def name_change_action(request):
    context = {
        'page':'manage_account'
    }

    form = ChangeNameForm(request.POST)

    if not form.is_valid():
        raise Http404

    new_fname = form.cleaned_data['new_fname']
    new_lname = form.cleaned_data['new_lname']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username = user.username , password = password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(context,"pages/user_account.html",context)

    #proceed and change the name
    
    user.first_name = new_fname
    user.last_name = new_lname
    user.save()

    context['success']= render_to_string('objects/notifications/profile/changed_object.html',{ 'changed_object': "first and last name" })
    
    return render(request,"pages/user_account.html",context)

