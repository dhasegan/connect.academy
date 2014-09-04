import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from django.core.urlresolvers import reverse

from app.models import *
from app.context_processors import *
from app.forms import *

def welcome(request):
    if request.user and request.user.is_authenticated():
        return redirect('/home')

    context = {
        "page": "welcome",
    }
    return render(request, "pages/welcome_page.html", context)



@login_required
def dashboard(request):
    context = {
        'page': 'dashboard',
        'user_auth': request.user.juser
    }

    context = dict(context.items() + dashboard_context(request).items())

    # if not len(context['activities']) and not len(context['schedule_items']) and \
    #     not len(context['courses']) and not len(context['forum_posts']):
    #         return redirect( reverse('explore') )

    return render(request, "pages/dashboard.html", context)


@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
    }
    context['comments'] = Review.objects.all()

    return render(request, 'pages/comments.html', context)

def conduct_code(request):
    context = {
        'page': 'conduct_code'
    }

    return render(request, 'pages/conduct_code.html', context)

def error_page(request, error_type):
    context = {
        'page': 'error_page',
        'error_type': error_type
    }
    return HttpResponse(json.dumps(context))

@login_required
def load_dashboard_activities(request):
    user = request.user.juser
    activities = dashboard_activities(request,user)
    html = render_to_string('objects/dashboard/activity_timeline.html', 
                            { "activities" : activities, 
                               "user_auth": user
                            })
    data = {
        'status': "OK",
        'html': html
    }

    return HttpResponse(json.dumps(data))

@login_required
def load_new_dashboard_activities(request):
    user = request.user.juser
    activities = new_dashboard_activities(request,user)
    context = { "activities" : activities, "user_auth": user }
    context.update(csrf(request))
    html = render_to_string('objects/dashboard/activity_timeline.html', context  )
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

@require_POST
def add_subscriber(request):
    context = {
        'page': 'welcome',
    }
    context.update(csrf(request))

    form = NewSubscriberForm(request.POST)
    if not form.is_valid():
        
        context['error'] = "Failed to process request:"
        for error in form.non_field_errors():
            context['error'] += " " + str(error) + ", "
        for error in form.email.field_errors():
            context['error'] += " " + str(error) + ", "
        for error in form.name.field_errors():
            context['error'] += " " + str(error) + ", "

        return render(request, "pages/welcome_page.html", context)


    name = form.cleaned_data['name']
    email = form.cleaned_data['email']

    Subscriber.objects.create(name=name, email=email)

    context['success'] = "Thank you for your interest :)"

    return render(request, "pages/welcome_page.html", context)