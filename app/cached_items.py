
from django.core.cache import cache

from app.models import *
from app.explore.context_processors import *

explore_page_context_key = "explore-page"


def cache_explore_context():
    ckey = explore_page_context_key
    explore_context = cache.get(ckey)
    if not explore_context:
        courses = Course.objects.all()
        explore_context = course_timeline_context(courses, None)
        cache.set(ckey, explore_context, 55 * 60)  # cache for 55 minutes

    return explore_context


def category_create_key(checked_categories):
    key = "categories"
    cats = sorted(checked_categories)
    for cat in cats:
        key = key + '-' + str(cat)
    return key


def cache_categories(checked):
    ckey = category_create_key(checked)
    categories_context = cache.get(ckey)
    if not categories_context:
        categories_context = explore_categories_context(checked)
        cache.set(ckey, categories_context, 24 * 60 * 60)

    return categories_context
