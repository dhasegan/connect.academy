from django.core.context_processors import csrf
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string 
from django.core.urlresolvers import reverse
 
from app.models import *
from app.profile.forms import *
from app.profile.context_processors import *
from app.decorators import *
from app.helpers import *
from app.messages import *

import json

@require_GET
@login_required
def profile(request, username):
    user = get_object_or_404(jUser, username=username)
    current_user = get_object_or_404(jUser, id=request.user.id)

    context = {
        'page': 'profile'
    }
    
    context['user'] = user
    if user.is_professor():
        registrations = ProfessorCourseRegistration.objects.filter(professor=user, is_approved=True)
        context['courses_managed'] = [reg.course for reg in registrations]
    context['own_profile'] = current_user.id == user.id
    context['activities'] = profile_activities(request, user, current_user)

    response = render(request, "pages/profile.html", context)
    if context['activities']:
        response.set_cookie("oldest_activity_id", str(context['activities'][-1]['activity'].id), path="/")

    return response


@login_required
def load_profile_activities(request, username):
    user = get_object_or_404(jUser,username=username)
    current_user = get_object_or_404(jUser, id=request.user.id)
    
    activities = profile_activities(request,user, current_user)
    if len(activities) == 0:
        return HttpResponse(json.dumps({
            'status': "OK",
            'html': ""
        }))
    context = { 
        "activities" : activities , 
        "user_auth": request.user.juser
    }
    html = render_to_string('objects/dashboard/activity_timeline.html', context)
    data = {
        'status': "OK",
        'html': html
    }

    response = StreamingHttpResponse(json.dumps(data))
    if activities:
        response.set_cookie("oldest_activity_id", str(activities[-1]['activity'].id), path="/")

    return response

@login_required
def load_new_profile_activities(request, username):
    user = get_object_or_404(jUser, username=username)
    current_user = get_object_or_404(jUser, id=request.user.id)
    activities = new_profile_activities(request, user, current_user)

    context = { 
        "activities" : activities,
        "user_auth": request.user.juser
    } 
    html = render_to_string('objects/dashboard/activity_timeline.html', context)
    data = {
        'status': "OK",
        'html': html,
    }
    if activities:
        data['new_last_id'] = activities[0]['activity'].id

    return HttpResponse(json.dumps(data))


@require_GET
@login_required
def manage_account(request):
    context = {
        'page': 'manage_account'
    }

    for message in get_messages(request):
        if message.extra_tags == "hidden":
            if message.message.startswith(PREFIX_MANAGE_ACCOUNT_ERROR):
                error_strings = message.message.replace(PREFIX_MANAGE_ACCOUNT_ERROR, "").split("<!>")
                context['error'] = "<br/>".join(error_strings)

    if "page_id" in request.GET:
        context["page_id"] = request.GET["page_id"]
    return render(request, "pages/auth/manage_account.html", context)


@require_POST
@login_required
def username_change_action(request):
    user = get_object_or_404(jUser, id=request.user.id)
    redirect_url = reverse("welcome")
    
    form = ChangeUsernameForm(request.POST)
    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_MANAGE_ACCOUNT_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect(redirect_url)

    new_username = form.cleaned_data['new_username']
    password = form.cleaned_data['password']

    auth_user = authenticate(username=user.username, password=password)
    if not auth_user:
        error_message = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        messages.error(request, error_message)
        return redirect(redirect_url)

    # proceed and change the username.
    if jUser.objects.filter(username=new_username).count() > 0:
        error_message = render_to_string('objects/notifications/profile/username_exists.html', {})
        messages.error(request, error_message)
        return redirect(redirect_url)

    user.username = new_username
    user.save()

    success_message = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "username"})
    messages.success(request, success_message)
    return redirect(redirect_url)


@require_POST
@login_required
def password_change_action(request):
    form = ChangePasswordForm(request.POST)
    redirect_url = reverse('manage_account') + "?page_id=change_password"

    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_MANAGE_ACCOUNT_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect(redirect_url)

    old_password = form.cleaned_data['old_pass']
    new_password = form.cleaned_data['new_pass']
    confirm_pass = form.cleaned_data['confirm_new_pass']

    user = request.user
    user = authenticate(username=user.username, password=old_password)

    if not user or new_password != confirm_pass:
        error_message = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        messages.error(request, error_message)
        return redirect(redirect_url)

    user.set_password(new_password)
    user.save()

    success_message = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "password"})
    messages.success(request, success_message)
    return redirect(redirect_url)


@require_POST
@login_required
def name_change_action(request):
    form = ChangeNameForm(request.POST)
    redirect_url = reverse('manage_account') + "?page_id=change_name"

    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_MANAGE_ACCOUNT_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect(redirect_url)

    new_fname = form.cleaned_data['new_fname']
    new_lname = form.cleaned_data['new_lname']
    password = form.cleaned_data['password']

    user = request.user
    user = authenticate(username=user.username, password=password)

    if not user:
        error_message = render_to_string('objects/notifications/profile/incorrect_password.html', {})
        messages.error(request, error_message)
        return redirect(redirect_url)

    user.first_name = new_fname
    user.last_name = new_lname
    user.save()

    success_message = render_to_string('objects/notifications/profile/changed_object.html', {'changed_object': "first and last name"})
    messages.success(success_message)
    return redirect( revert('manage_account') )


@login_required
@require_active_user
def new_profile_picture(request):
    form = ProfilePictureForm(request.POST, request.FILES)
    redirect_url = reverse('manage_account') + "?page_id=change_profile_picture"

    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_MANAGE_ACCOUNT_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect(redirect_url)

    user = request.user.juser
    user.profile_picture = form.cleaned_data['picture']
    user.save()

    return redirect( reverse("profile", args=(user.username, )) )


@login_required
@require_active_user
def edit_summary(request):
    form = EditSummaryForm(request.POST)
    redirect_url = reverse('profile', args=(request.user.username,))

    if not form.is_valid():
        error_message = serialize_form_errors(request, form, PREFIX_MANAGE_ACCOUNT_ERROR)
        messages.error(request, error_message, extra_tags="hidden")
        return redirect(redirect_url)

    summary = form.cleaned_data['summary']
    user = request.user.juser

    user.summary = summary
    user.save()

    html = render_to_string('objects/profile/summary.html', {"user": user, "own_profile":True})
    context = {
        "status": "OK",
        "html" : html,
    }
    return HttpResponse(json.dumps(context))
