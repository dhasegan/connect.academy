import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings

from app.models import *
from app.context_processors import *


def welcome(request):
    if request.user and request.user.is_authenticated():
        return redirect('/home')

    context = {
        "page": "welcome",
    }
    return render(request, "pages/welcome_page.html", context)


def about(request):
    context = {
        "page": "about",
    }
    return render(request, "pages/about.html", context)


@login_required
def dashboard(request):
    context = {
        'page': 'dashboard',
    }

    context = dict(context.items() + dashboard_context(request).items())

    return render(request, "pages/dashboard.html", context)


@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
    }
    context['comments'] = Review.objects.all()

    return render(request, 'pages/comments.html', context)


def error_page(request, error_type):
    context = {
        'page': 'error_page',
        'error_type': error_type
    }

@login_required
def load_dashboard_activities(request):
    user = request.user.juser
    activities = dashboard_activities(request,user)
    html = render_to_string('objects/dashboard/activity_timeline.html', { "activities" : activities} )
    data = {
        'status': "OK",
        'html': html
    }

    return HttpResponse(json.dumps(data))

@login_required
def load_new_dashboard_activities(request):
    user = request.user.juser
    activities = new_dashboard_activities(request,user)
    html = render_to_string('objects/dashboard/activity_timeline.html', { "activities" : activities} )
    data = {
        'status': "OK",
        'html': html,
    }
    if activities:
        data['new_last_id'] = activities[0]['activity'].id

    return HttpResponse(json.dumps(data))

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'pages/set_timezone.html', {'timezones': pytz.common_timezones})