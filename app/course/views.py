from mimetypes import guess_type
import hashlib
import string
import random

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

from app.models import *
from app.course_info import *
from app.context_processors import *
from app.course.forms import *


@require_GET
@login_required
def course_page(request, slug):
    course = get_object_or_404(Course, slug=slug)
    context = {
        "page": "course",
    }
    context = dict(context.items() + course_page_context(request, course).items())

    return render(request, "pages/course.html", context)


@require_GET
@login_required
def get_course_image(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not course.image:
        raise Http404

    content_type = guess_type(course.image.name)
    return HttpResponse(course.image, mimetype=content_type)


@require_POST
@login_required
def submit_comment(request, slug):

    form = SubmitCommentForm(request.POST)
    if not form.is_valid():
        raise Http404

    course = form.cleaned_data['course']

    comment_text = form.cleaned_data['comment']
    comment = Review(course=course, review=comment_text)
    comment.save()

    return redirect(form.cleaned_data['url'])


@require_POST
@login_required
def rate_course(request, slug):
    context = {}

    user = get_object_or_404(jUser, id=request.user.id)

    form = RateCourseForm(request.POST)
    if not form.is_valid():
        raise Http404

    course = form.cleaned_data['course']
    rating_value = form.cleaned_data['rating_value']
    rating_type = form.cleaned_data['rating_type']

    if rating_type != PROFESSOR_R:
        ratings = Rating.objects.filter(user=user, course=course, rating_type=rating_type)
        if len(ratings) == 0:
            rating = Rating(user=user, course=course, rating=rating_value, rating_type=rating_type)
            rating.save()
        else:
            rating = ratings[0]
            rating.rating = rating_value
            rating.save()
    else:
        prof = form.cleaned_data['prof']
        ratings = Rating.objects.filter(user=user, course=course, rating_type=rating_type, professor=prof)
        if len(ratings) == 0:
            rating = Rating(user=user, course=course, rating=rating_value, rating_type=rating_type, professor=prof)
            rating.save()
        else:
            rating = ratings[0]
            rating.rating = rating_value
            rating.save()

    return redirect(form.cleaned_data['url'])

@require_POST
@login_required
def submit_document(request, slug):
    context = {}

    user = get_object_or_404(jUser, id=request.user.id)

    form = SubmitDocumentForm(request.POST, request.FILES)

    if not form.is_valid():
        raise Http404

    if not user in form.cleaned_data['course'].professors.all():
        raise Http404

    docfile = form.cleaned_data['document']
    course_document = CourseDocument(document=docfile, name=form.cleaned_data['name'],
        course=form.cleaned_data['course'], submitter=user)
    course_document.save()

    return redirect(form.cleaned_data['url'])
