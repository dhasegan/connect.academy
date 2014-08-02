import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string

from app.models import *
from app.explore.context_processors import *


@login_required
def explore(request):
    context = {
        "page": "explore",
    }

    courses = Course.objects.all()
    context = dict(context.items() + course_timeline_context(courses, request.user).items())
    return render(request, "pages/explore.html", context)


@login_required
@require_POST
def explore_categories(request):
    checked = []
    for key, value in request.POST.iteritems():
        if key.isdigit():
            checked.append(int(key))
    context = {
        'explore_categories': explore_categories_context(checked)
    }
    response_data = {}
    response_data['html'] = render_to_string("objects/explore/categories.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")
