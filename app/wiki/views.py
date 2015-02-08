from mimetypes import guess_type
import hashlib
import string
import random
import datetime

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

# ContentType is needed for version control
from django.contrib.contenttypes.models import ContentType
from versioning.models import *

from app.models import *
from app.context_processors import *
from app.wiki.forms import *
from app.decorators import *


#@transaction.atomic()
#@reversion.create_revision()
@require_GET
@require_active_user
@login_required
def edit_wiki_page(request, slug):
    context = {
        "page": "edit_wiki_page",
        'slug': slug,
    }
    course = Course.objects.get(slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not course.can_edit_wiki(user):
        raise Http404


    if hasattr(course, 'wiki'):
        wiki = course.wiki
        
        context['course'] = course
        context['content'] = wiki.content

    else:
        context['course'] = course
        professors = []
        for reg in ProfessorCourseRegistration.objects.filter(course=course, is_approved=True):
            professors.append(reg.professor)

        wiki_context = {
            'course': course,
            'professors': professors,
            'registered_students': StudentCourseRegistration.objects.filter(course=course,
                                                                            is_approved=True).count(),
            'pending_students': StudentCourseRegistration.objects.filter(course=course,
                                                                         is_approved=False).count()
        }
        context['content'] = render_to_string('objects/wiki/default_content.html', RequestContext(request, wiki_context))

    return render(request, "pages/wiki/edit_wiki_page.html", context)


#@transaction.atomic()
#@reversion.create_revision()
@require_POST
@require_active_user
@login_required
def save_wiki_page(request, slug):
    context = {
        "page": "edit_wiki_page",  # it will be rendered on edit_wiki_page
        "slug": slug,
    }
    context.update(csrf(request))
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not course.can_edit_wiki(user):
        raise Http404

    form = WikiPageForm(request.POST)
    if not form.is_valid():
        raise Http404

    content = form.cleaned_data['content']
    if hasattr(course, 'wiki'):
        # update content
        wiki = course.wiki
        wiki.content = content
        wiki.save()

        context['success'] = render_to_string('objects/notifications/wiki/wiki_edited.html', {
            'course_name': course.name
        })
    else:
        wiki = WikiPage.objects.create(course=course, content=content)
        context['success'] = render_to_string('objects/notifications/wiki/wiki_created.html', {
            'course_name': course.name
        })


    wiki_ctype = ContentType.objects.get(app_label="app", model="wikipage")
    content_object = wiki_ctype.get_object_for_this_type(pk=wiki.id)
    revision = Revision.objects.filter(content_type=wiki_ctype, object_id=content_object.pk).latest('created_at')
    WikiContributions.objects.create(wiki=wiki, user=user, revision=revision)

    context['course'] = course
    context['content'] = wiki.content

    return render(request, 'pages/wiki/edit_wiki_page.html', context)


@login_required
@require_active_user
def revert_wiki_page(request):
    pass


@login_required
def view_wiki_page(request, slug):
    context = {
        'page': 'view_wiki_page',
    }
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not hasattr(course, 'wiki'):
        raise Http404

    wiki = course.wiki
    context['wiki'] = wiki
    context['can_edit_wiki'] = course.can_edit_wiki(user)
    context['course'] = course

    wiki_type_id = ContentType.objects.get(app_label="app", model="wikipage").id
    context['wiki_type_id'] = wiki_type_id

    return render(request, 'pages/wiki/view_wiki.html', context)
