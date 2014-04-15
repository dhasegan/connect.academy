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
from app.helpers import *
import hashlib
import string
import random

# Mimetypes for images
from mimetypes import guess_type

# App Models
from app.models import *
from app.course_info import *
from app.context_processor import *
from app.profile.forms import *
from app.campusnet_login import *


@login_required
def profile(request,username):
    # stub for profile view
    context = {'page': 'profile'}
    context['user_auth'] = user_authenticated(request)
    user = jUser.objects.filter(username=username)
    if user:
        user = user[0] 
        context['user'] = user

    return render(request,"pages/profile.html",context)


@login_required
def manage_account(request):

    context = {'page':'home'}
    context['user_auth'] = user_authenticated(request)

    return render(request,"pages/user_account.html",context)


@login_required
def password_change_action(request):
    
    context = {'page':'manage_account'}
    context['user_auth'] = user_authenticated(request)
    context.update(csrf(request))

    if request.method!='POST':
        raise Http404

    form = ChangePasswordForm(request.POST)
    
    if not form.is_valid():
        raise Http404

    old_password = form.cleaned_data['old_pass']
    new_password = form.cleaned_data['new_pass']
    confirm_pass = form.cleaned_data['confirm_new_pass']

    user = request.user
    user = authenticate(username = user.username, password = old_password)

    if not user:
        context['error'] = 'Your <b>password</b> is <b>incorrect</b>. Please check your password and try again.'
        return render(request,"pages/user_account.html",context)

    if new_password != confirm_pass:
        context['error'] = 'Your <b>passwords</b> do <b>not match</b>. Please check your passwords and try again.'
        return render(request,"pages/user_account.html",context)

    #everything went fine

    user.set_password(new_password)
    user.save()
    context['success'] = 'Your <b>password</b> has been changed <b>successfully</b> !'


    return render(request,"pages/user_account.html",context)

@login_required
def username_change_action(request):
    context = {'page':'manage_account'}
    context['user_auth'] = user_authenticated(request)
    context.update(csrf(request))

    if request.method!='POST':
        raise Http404

    form = ChangeUsernameForm(request.POST)

    if not form.is_valid():
        raise Http404

    new_username = form.cleaned_data['new_username']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username=user.username, password = password)

    if not user:
        context['error'] = 'Your <b>password</b> is <b>incorrect</b>. Please check your password and try again.'
        return render(request,"pages/user_account.html",context)

    #proceed and change the username.

    user.username = new_username
    user.save()

    context['success'] = 'Your <b>username</b> has been changed <b> successfully</b> !'

    return render(request,"pages/user_account.html",context)

@login_required
def name_change_action(request):
    context = {'page':'manage_account'}
    context['user_auth'] = user_authenticated(request)
    context.update(csrf(request))

    if request.method!='POST':
        raise Http404

    form = ChangeNameForm(request.POST)

    if not form.is_valid():
        raise Http404

    new_fname = form.cleaned_data['new_fname']
    new_lname = form.cleaned_data['new_lname']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username = user.username , password = password)

    if not user:
        context['error'] = 'Your <b>password</b> is <b>incorrect</b>. Please check your password and try again. '
        return render(context,"pages/user_account.html",context)

    #proceed and change the name
    
    user.first_name = new_fname
    user.last_name = new_lname
    user.save()

    context['success']='Your <b>first</b> and <b>last</b> name have been changed <b>successfully</b> !'
    
    return render(request,"pages/user_account.html",context)

