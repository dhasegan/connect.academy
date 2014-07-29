import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

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
        'user_auth': request.user
    }
    user = request.user
    context['courses'] = []

    if user.user_type == USER_TYPE_STUDENT:
        registrations = StudentCourseRegistration.objects.filter(student=user)
        for reg in registrations:
            context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved})

    elif user.user_type == USER_TYPE_PROFESSOR:
        registrations = ProfessorCourseRegistration.objects.filter(professor=user)
        for prof_reg in registrations:  # for each professor registration
            course_dict = {'course': prof_reg.course,
                           'is_approved': prof_reg.is_approved}
            if prof_reg.is_approved:
                course_dict['students'] = {'registered': [], 'pending': []}
                # for each student registration
                for student_reg in StudentCourseRegistration.objects.filter(course=prof_reg.course):
                    if student_reg.is_approved:
                        course_dict['students']['registered'].append(student_reg.student)
                    else:
                        course_dict['students']['pending'].append(student_reg.student)
                course_dict['documents'] = prof_reg.course.coursedocument_set.all()
                course_dict['homework'] = prof_reg.course.coursehomeworkrequest_set.all()
                course_dict['forum'] = None
                forums = prof_reg.course.forumcourse_set.all()
                if forums.count() == 1:
                    course_dict['forum'] = forums[0]
            context['courses'].append(course_dict)

    else:
        return redirect('/admin')

    return render(request, "pages/dashboard.html", context)


@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
    }
    context['comments'] = Review.objects.all()

    return render(request, 'pages/comments.html', context)


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