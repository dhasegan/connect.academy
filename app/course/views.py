from mimetypes import guess_type
import hashlib
import string
import random
import datetime
import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string

from app.models import *
from app.course.context_processors import *
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
def submit_review(request, slug):

    form = SubmitCommentForm(request.POST)
    if not form.is_valid():
        raise Http404

    user = get_object_or_404(jUser, id=request.user.id)

    course = form.cleaned_data['course']

    comment_text = form.cleaned_data['comment']
    comment = Review(course=course, review=comment_text, posted_by=user,
                     anonymous=form.cleaned_data['anonymous'])
    comment.save()
    comment.upvoted_by.add(user)

    context = {
        'course': course,
        'comment': review_context(comment, user)
    }
    response_data = {}
    response_data['html'] = render_to_string("objects/course/review.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_POST
@login_required
def rate_course(request, slug):
    user = get_object_or_404(jUser, id=request.user.id)

    form = RateCourseForm(request.POST)
    if not form.is_valid():
        raise Http404

    course = get_object_or_404(Course, slug=slug)
    course_form = form.cleaned_data['course']
    if course.id != course_form.id:
        raise Http404

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


    context = {
        'course': course,
        'ratings': course_ratings_context(course, user)
    }
    response_data = {}
    response_data['ratings'] = render_to_string("objects/course/ratings.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
                                     description=form.cleaned_data['description'], course=form.cleaned_data['course'], 
                                     submitter=user, course_topic=form.cleaned_data["topic"])
    course_document.save()

    return redirect(form.cleaned_data['url'])


@require_POST
@login_required
def submit_homework(request, slug):
    context = {}

    user = get_object_or_404(jUser, id=request.user.id)

    form = SubmitHomeworkForm(request.POST, request.FILES)

    if not form.is_valid():
        raise Http404

    course = form.cleaned_data['course']
    registration_status = course.get_registration_status(user)
    if registration_status != COURSE_REGISTRATION_REGISTERED:
        raise Http404

    homework_request = form.cleaned_data['homework_request']

    previous_homework = CourseHomeworkSubmission.objects.filter(submitter=user, homework_request=homework_request)
    for prev_hw in previous_homework:
        prev_hw.delete()

    docfile = form.cleaned_data['document']
    course_homework = CourseHomeworkSubmission(document=docfile, course=form.cleaned_data['course'],
                                               submitter=user, homework_request=homework_request)
    course_homework.save()

    return redirect(form.cleaned_data['url'])


@require_POST
@login_required
def submit_homework_request(request, slug):
    context = {}

    user = get_object_or_404(jUser, id=request.user.id)

    form = SubmitHomeworkRequestForm(request.POST)

    if not form.is_valid():
        raise Http404

    if not user in form.cleaned_data['course'].professors.all():
        raise Http404

    timezone_minutes = timedelta(minutes=form.cleaned_data['timezone'])
    start_time = form.cleaned_data['start'] + timezone_minutes
    end_time = form.cleaned_data['deadline'] + timezone_minutes

    deadline = Deadline(start=start_time, end=end_time)
    deadline.save()
    homework_request = CourseHomeworkRequest(name=form.cleaned_data['name'], description=form.cleaned_data['description'],
                                             course=form.cleaned_data['course'], submitter=user, 
                                             deadline=deadline, course_topic=form.cleaned_data["topic"])
    homework_request.save()

    return redirect(form.cleaned_data['url'])


@require_POST
@login_required
def vote_review(request, slug):
    context = {}

    user = get_object_or_404(jUser, id=request.user.id)

    form = VoteReviewForm(request.POST)

    if not form.is_valid():
        raise Http404

    review = form.cleaned_data['review']

    if form.cleaned_data['vote_type'] == "upvote":
        if not review.upvoted_by.filter(username=user.username).count():
            review.upvoted_by.add(user)
        else:
            review.upvoted_by.remove(user)
    if form.cleaned_data['vote_type'] == "downvote":
        if not review.upvoted_by.filter(username=user.username).count():
            review.downvoted_by.add(user)
        else:
            raise Http404

    context = {
        'course': review.course,
        'comment': review_context(review, user)
    }
    response_data = {}
    response_data['html'] = render_to_string("objects/course/upvote_review.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def register_course(request, slug):
    context = {
        "page": "register_course"
    }
    context.update(csrf(request))
    user = request.user
    course = get_object_or_404(Course, slug=slug)
    registration_deadline = course.get_registration_deadline()
    registration_status = course.get_registration_status(user)
    registration_open = registration_deadline.is_open() if registration_deadline is not None else False

    if user.user_type == USER_TYPE_STUDENT:
        if registration_open:
            if registration_status == COURSE_REGISTRATION_OPEN:
                course_registration = StudentCourseRegistration(student=user,
                                                                course=course,
                                                                is_approved=False)
                course_registration.save()
                return HttpResponse("OK", context)
            elif registration_status in [COURSE_REGISTRATION_PENDING, COURSE_REGISTRATION_REGISTERED]:
                return HttpResponse("You have already registered for this course.", context)
            elif registration_status == COURSE_REGISTRATION_NOT_ALLOWED:
                return HttpResponse("You are not allowed to register for this course")
        else:
            return HttpResponse("Course registration period is not open.")
    elif user.user_type == USER_TYPE_PROFESSOR:
        if registration_status == COURSE_REGISTRATION_OPEN:
                course_registration = ProfessorCourseRegistration(professor=user,
                                                                  course=course,
                                                                  is_approved=False)
                course_registration.save()
                return HttpResponse("OK", context)
        elif registration_status in [COURSE_REGISTRATION_PENDING, COURSE_REGISTRATION_REGISTERED]:
            return HttpResponse("You have already registered for this course.", context)
        elif registration_status == COURSE_REGISTRATION_NOT_ALLOWED:
            return HttpResponse("You are not allowed to register for this course.")
    else:
        return HttpResponse("You are not allowed to register for this course.")


@require_POST
@login_required
def send_mass_email(request, slug):
    course = get_object_or_404(Course, slug=slug)

    context = {
        'page': 'send_mass_email',
        'user_auth': request.user
    }
    context.update(csrf(request))

    # Make sure the logged in user is allowed to approve these registrations
    user = request.user
    subject = request.POST['subject']
    body = request.POST['email']
    to = []
    sender = "%s %s <%s>" % (user.first_name, user.last_name, user.email)
    for key, val in request.POST.items():
        if 'user' in key:
            _, user_id = key.split('-')
            users = jUser.objects.filter(id=user_id)
            if users is not None and val:  # if user exists (users is not None) and checkbox was checked (val)
                email = users[0].email
                to.append(email)

    if len(to) > 0:
        send_mail(subject, body, sender, to, fail_silently=False)
        return HttpResponse("OK")
    else:
        return HttpResponse("Please select at least one recepient.")
