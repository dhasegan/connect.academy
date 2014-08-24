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

explore_page_context_key = "explore-page"

@login_required
def explore(request):
    context = {
        "page": "explore",
    }

    user = get_object_or_404(jUser, id=request.user.id)

    ckey = explore_page_context_key
    explore_context = cache.get(ckey)
    if not explore_context:
        courses = Course.objects.all()
        explore_context = course_timeline_context(courses, user)
        cache.set(ckey, explore_context, 60*60)

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

    ckey = category_create_key(checked)
    categories_context = cache.get(ckey)
    if not categories_context:
        categories_context = explore_categories_context(checked)
        cache.set(ckey, categories_context, 60 * 60)
    context['explore_categories'] = categories_context

    response_data = {}
    response_data['html'] = render_to_string("objects/explore/categories.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def category_create_key(checked_categories):
    key = "categories"
    cats = sorted(checked_categories)
    for cat in cats:
        key = key + '-' + str(cat)
    return key