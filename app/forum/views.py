import json

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from app.models import *
from app.context_processors import *
from app.course.forms import *


@require_GET
@login_required
def forum_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    context = {
        "page": "forum_course",
    }
    return render(request, "pages/forum_page.html", context)


@require_POST
@login_required
def forum_course_registration(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not user.is_professor_of(course):
        raise Http404

    forums = course.forumcourse_set.all()
    if forums.count():
        raise Http404

    forum = ForumCourse(forum_type=FORUM_TYPE_COURSE, course=course)
    forum.save()

    response_data = {}
    response_data['html'] = render_to_string("objects/forum/forum_management.html", {})
    return HttpResponse(json.dumps(response_data), content_type="application/json")
