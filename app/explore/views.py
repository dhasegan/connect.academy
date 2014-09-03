import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from app.models import *
from app.explore.context_processors import *
from app.cached_items import cache_explore_context, cache_categories

@login_required
def explore(request):
    context = {
        "page": "explore",
    }

    user = get_object_or_404(jUser, id=request.user.id)
    explore_context = cache_explore_context()

    uni_category = user.university.get_university_category()
    context['explore_categories'] = explore_categories_context([uni_category.id])

    context = dict(context.items() + explore_context.items())
    return render(request, "pages/explore.html", context)


@login_required
@require_POST
def explore_categories(request):
    context = {}
    checked = []
    for key, value in request.POST.iteritems():
        if key.isdigit():
            checked.append(int(key))

    context['explore_categories'] = cache_categories(checked)

    response_data = {}
    response_data['html'] = render_to_string("objects/explore/categories.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")
