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


from app.models import *
from app.context_processors import *
from app.wiki.forms import *


#@transaction.atomic()
#@reversion.create_revision()
@login_required
def edit_wiki_page(request, slug):
    context = {
        "page": "edit_wiki_page",
        'slug': slug,
    }
    course = Course.objects.get(slug=slug)
    wikis = course.wiki.all()
    user = request.user
    if user.university != course.university or not user.is_active:
        raise Http404

    if len(wikis) > 0:
        wiki = wikis[0]
        context['course'] = course
        context['content'] = wiki.content

    else:
        context['course'] = course
        professors = []
        for reg in ProfessorCourseRegistration.objects.filter(course=course, is_approved=True):
            professors.append(reg.professor)
        context['content'] = render_to_string('objects/wiki/default_content.html', {
            'STATIC_URL': "/static/",
            'course': course,
            'professors': professors,
            'registered_students': StudentCourseRegistration.objects.filter(course=course,
                                                                            is_approved=True).count(),
            'pending_students': StudentCourseRegistration.objects.filter(course=course,
                                                                         is_approved=False).count()
            
        })

    return render(request, "pages/wiki/edit_wiki_page.html", context)


#@transaction.atomic()
#@reversion.create_revision()
@require_POST
@login_required
def save_wiki_page(request, slug):
    context = {
        "page": "edit_wiki_page",  # it will be rendered on edit_wiki_page
        "slug": slug,
    }
    context.update(csrf(request))
    course = get_object_or_404(Course, slug=slug)
    user = request.user

    # Only users from that university are allowed to edit
    # wiki pages
    if user.university != course.university or not user.is_active:
        raise Http404

    form = WikiPageForm(request.POST)
    if not form.is_valid():
        raise Http404

    content = form.cleaned_data['content']
    wikis = course.wiki.all()
    if wikis:
        # update content
        wiki = wikis[0]
        wiki.content = content
        wiki.save()
        # add student contribution if it doesn't exist
        # if it exists, change the date
        contribs = WikiContributions.objects.filter(wiki=wiki,
                                                    user=user)
        if contribs:
            # the 'modified_by' field has the auto_now keyword,
            # so it will be updated automatically when calling save()
            contribs[0].save()
        else:
            WikiContributions.objects.create(wiki=wiki,
                                             user=user).save()
        context['success'] = render_to_string('objects/notifications/wiki/wiki_edited.html', {
            'course_name': course.name
        })
    else:
        wiki = WikiPage.objects.create(course=course, content=content)
        wiki.save()
        WikiContributions.objects.create(wiki=wiki,
                                         user=user).save()
        context['success'] = render_to_string('objects/notifications/wiki/wiki_created.html', {
            'course_name': course.name
        })

    context['course'] = course
    context['content'] = wiki.content

    return render(request, 'pages/wiki/edit_wiki_page.html', context)


@login_required
def revert_wiki_page(request):
    pass


@login_required
def view_wiki_page(request, slug):
    context = {
        'page': 'view_wiki_page',
    }
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    wikis = course.wiki.all()
    context['can_edit_wiki'] = None
    if len(wikis) < 1:
        raise Http404
    else:
        wiki = wikis[0]
        context['wiki'] = wiki
        context['course'] = wiki.course
        wiki_type_id = ContentType.objects.get(app_label="app", model="wikipage").id
        context['wiki_type_id'] = wiki_type_id
        context['can_edit_wiki'] = wiki.can_edit(user)

    return render(request, 'pages/wiki/view_wiki.html', context)
