import json

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.template import Context, Template, RequestContext


from app.models import *
from app.context_processors import *
from app.forum.forms import *


@require_GET
@login_required
def forum_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    context = {
        "page": "forum_course",
    }
    context["course"] = course

    forums = course.forumcourse_set.all()
    if not forums.count():
        raise Http404
    context = dict(context.items() + forum_context(forums[0], user).items())

    return render(request, "pages/forum/page.html", context)


@require_POST
@login_required
def course_registration(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not user.is_professor_of(course):
        raise Http404

    forums = course.forumcourse_set.all()
    if forums.count():
        raise Http404

    forum = ForumCourse(forum_type=FORUM_TYPE_COURSE, course=course)
    forum.save()

    context = {
        'course': {
            'course': course
        }
    }
    response_data = {}
    response_data['html'] = render_to_string("objects/forum/forum_management.html", RequestContext(request, context))
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@require_http_methods(["GET", "POST"])
@login_required
def new_post(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)
    context = {
        "page": "forum_new_post"
    }
    context["course"] = course

    forums = course.forumcourse_set.all()
    if not forums.count():
        raise Http404
    context['forum'] = forums[0]

    # Get request
    if request.method == "GET":
        return render(request, "pages/forum/new_post.html", context)
    
    # Post request
    form = SubmitForumPost(request.POST)
    if not form.is_valid():
        raise Http404

    # user permissions to post:
    # everyone is allowed

    post = ForumPost(name=form.cleaned_data['title'], forum=form.cleaned_data['forum'],
                    text=form.cleaned_data['description'], posted_by=user,
                    anonymous=form.cleaned_data['anonymous'])
    post.save()

    return redirect("app.forum.views.forum_course", slug=course.slug)


@require_POST
@login_required
def new_answer(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)
    context = {}
    context["course"] = course

    forums = course.forumcourse_set.all()
    if not forums.count():
        raise Http404
    
    form = SubmitForumAnswer(request.POST)
    if not form.is_valid():
        raise Http404

    # user permissions to post:
    # everyone is allowed

    parent_answer = None
    if 'parent_answer' in form.cleaned_data and form.cleaned_data['parent_answer']:
        parent_answer = form.cleaned_data['parent_answer']

    answer = ForumAnswer(text=form.cleaned_data['text'], post=form.cleaned_data['post'],
                         parent_answer=parent_answer, posted_by=user, anonymous=form.cleaned_data['anonymous'])
    answer.save()

    if 'discussion_answer' in form.cleaned_data and form.cleaned_data['discussion_answer']:
        context = forum_discussion_context(forums[0], form.cleaned_data['post'], form.cleaned_data['discussion_answer'])
        template_filename = "objects/forum/discussion.html"
    else:
        context['forum'] = forums[0]
        context['post'] = forum_post_context(form.cleaned_data['post'])
        template_filename = "objects/forum/answers.html"

    response_data = {
        'html': render_to_string(template_filename, RequestContext(request, context)),
        'id_selector': '#answers' + str(form.cleaned_data['post'].id)
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@require_GET
@login_required
def reply_form(request, answer_id):
    answer = get_object_or_404(ForumAnswer, id=answer_id)
    user = get_object_or_404(jUser, id=request.user.id)

    post = answer.post
    forum = get_object_or_404(ForumCourse, id=post.forum.id)
    context = {
        'parent_answer': {
            'answer': answer,
            'child_answers': []
        },
        'question': post,
        'forum': forum,
        'course': forum.course
    }

    response_data = {
        'html': render_to_string("objects/forum/new_answer.html", RequestContext(request, context))
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@require_GET
@login_required
def discussion(request, answer_id):
    answer = get_object_or_404(ForumAnswer, id=answer_id)
    user = get_object_or_404(jUser, id=request.user.id)

    # Check if answer is exactly the second reply of a post
    parent_answer = answer.parent_answer
    if not parent_answer or parent_answer.parent_answer:
        raise Http404

    post = answer.post
    forum = get_object_or_404(ForumCourse, id=post.forum.id)
    context = forum_discussion_context(forum, post, answer)

    response_data = {
        'html': render_to_string("objects/forum/discussion.html", RequestContext(request, context))
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")
