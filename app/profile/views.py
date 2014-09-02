from django.core.context_processors import csrf
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string 
 
from app.models import *
from app.profile.forms import *
from app.profile.context_processors import *

import json

@require_GET
@login_required
def profile(request, username):
    # stub for profile view
    context = {
        'page': 'profile',
        'user_auth': request.user.juser
    }
    context.update(csrf(request))
    user = get_object_or_404(jUser, username=username)
    
    context['user'] = user
    context['own_profile'] = request.user.id == user.id
    context['activities'] = profile_activities(request,user)

    return render(request, "pages/profile.html", context)


@require_GET
@login_required
def manage_account(request):
    context = {
        'page': 'manage_account'
    }
    return render(request, "pages/auth/user_account.html", context)


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
    user = authenticate(username=user.username, password=old_password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(request, "pages/auth/user_account.html", context)

    if new_password != confirm_pass:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(request, "pages/auth/user_account.html", context)

    # everything went fine

    user.set_password(new_password)
    user.save()
    context['success'] = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "password"})

    return render(request, "pages/auth/user_account.html", context)


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

    user = authenticate(username=request.user.username, password=password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(request, "pages/auth/user_account.html", context)

    # proceed and change the username.
    if jUser.objects.filter(username=new_username).count() > 0:
        context['error'] = render_to_string('objects/notifications/profile/username_exists.html', {})
        return render(request, "pages/auth/user_account.html", context)
    user.username = new_username
    user.save()

    context['success'] = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "username"})

    return render(request, "pages/auth/user_account.html", context)


@require_POST
@login_required
def name_change_action(request):
    context = {
        'page': 'manage_account'
    }

    form = ChangeNameForm(request.POST)

    if not form.is_valid():
        raise Http404

    new_fname = form.cleaned_data['new_fname']
    new_lname = form.cleaned_data['new_lname']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username=user.username, password=password)

    if not user:
        context['error'] = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        return render(context, "pages/auth/user_account.html", context)

    # proceed and change the name

    user.first_name = new_fname
    user.last_name = new_lname
    user.save()

    context['success'] = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "first and last name"})

    return render(request, "pages/auth/user_account.html", context)



@login_required
def load_profile_activities(request, username):
    user = get_object_or_404(jUser,username=username)
    
    activities = profile_activities(request,user)

    html = render_to_string('objects/dashboard/activity_timeline.html',
                            { 
                                "activities" : activities , 
                                "user_auth": request.user.juser
                            })
    data = {
        'status': "OK",
        'html': html
    }

    return HttpResponse(json.dumps(data))

@login_required
def load_new_profile_activities(request, username):
    user = get_object_or_404(jUser, username=username)
    activities = new_profile_activities(request,user)

    html = render_to_string('objects/dashboard/activity_timeline.html', 
                            { 
                                "activities" : activities,
                                "user_auth": request.user.juser
                            } )
    data = {
        'status': "OK",
        'html': html,
    }
    if activities:
        data['new_last_id'] = activities[0]['activity'].id

    return HttpResponse(json.dumps(data))

@login_required
def edit_summary(request):
    form = EditSummaryForm(request.POST)
    if not form.is_valid():
        raise Http404

    summary = form.cleaned_data['summary']
    user = request.user.juser

    user.summary = summary
    user.save()

    html = render_to_string('objects/profile/summary.html', {"user": user, "own_profile":True})
    context = {
        "status": "OK",
        "html" : html,
    }
    #context.update(csrf(request))
    return HttpResponse(json.dumps(context))

@login_required
def new_profile_picture(request):
    form = ProfilePictureForm(request.POST, request.FILES)
    if not form.is_valid():
        raise Http404

    user = request.user.juser
    user.profile_picture = form.cleaned_data['picture']
    user.save()

    data = {
        'status': "OK",
        'image_url': user.profile_picture.url
    }

    return HttpResponse(json.dumps(data))