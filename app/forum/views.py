import json

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.template import Context, Template, RequestContext
from django.template.loader import render_to_string


from app.models import *
from app.forum.forms import *
from app.forum.context_processors import *


@require_GET
@login_required
def forum_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    context = {
        "page": "forum_course",
    }
    context["course"] = course

    forums = course.forum_set.all()
    if not forums.count():
        raise Http404
    forum = forums[0]
    context = dict(context.items() + forum_context(forum, user).items())

    if 'tag' in request.GET and request.GET['tag']:
        tag = request.GET['tag']
        if tag in forum.get_tags():
            context['current_tag'] = tag

    return render(request, "pages/forum/page.html", context)


@require_POST
@login_required
def course_registration(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    if not user.is_professor_of(course):
        raise Http404

    forums = course.forum_set.all()
    if forums.count():
        raise Http404

    forum = Forum(course=course)
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

    forums = course.forum_set.all()
    if not forums.count():
        raise Http404
    forum = forums[0]
    context['forum'] = forum
    context['tags'] = forum.get_tags()

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
                     anonymous=form.cleaned_data['anonymous'], tag=form.cleaned_data['tagsRadios'])
    post.save()

    return redirect("app.forum.views.forum_course", slug=course.slug)


@require_POST
@login_required
def new_answer(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)
    context = {}
    context["course"] = course

    forums = course.forum_set.all()
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
        context = forum_discussion_context(forums[0], form.cleaned_data['post'], form.cleaned_data['discussion_answer'], user)
        template_filename = "objects/forum/discussion.html"
    else:
        context['forum'] = forums[0]
        context['post'] = forum_post_context(form.cleaned_data['post'], user)
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
    forum = get_object_or_404(Forum, id=post.forum.id)
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
    forum = get_object_or_404(Forum, id=post.forum.id)
    context = forum_discussion_context(forum, post, answer, user)

    response_data = {
        'html': render_to_string("objects/forum/discussion.html", RequestContext(request, context))
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_GET
@login_required
def answers(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    user = get_object_or_404(jUser, id=request.user.id)

    forum = get_object_or_404(Forum, id=post.forum.id)
    context = {
        'course': forum.course,
        'forum': forum,
        'post': forum_post_context(post, user)
    }

    response_data = {
        'html': render_to_string("objects/forum/answers.html", RequestContext(request, context))
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_POST
@login_required
def upvote_post(request):
    user = get_object_or_404(jUser, id=request.user.id)

    form = UpvotePost(request.POST)
    if not form.is_valid():
        raise Http404

    post = form.cleaned_data['post']
    voted = len(post.upvoted_by.filter(id=user.id)) > 0
    if not voted:
        post.upvoted_by.add(user)
    else:
        post.upvoted_by.remove(user)

    context = {
        'post': {
            'question': post,
            'upvotes': len(post.upvoted_by.all()),
            'voted': not voted
        }
    }
    response_data = {
        'html': render_to_string('objects/forum/upvote_post.html', RequestContext(request, context)),
        'id_selector': '#upvote_post_' + str(post.id)
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_POST
@login_required
def upvote_answer(request):
    user = get_object_or_404(jUser, id=request.user.id)

    form = UpvoteAnswer(request.POST)
    if not form.is_valid():
        raise Http404

    answer = form.cleaned_data['answer']
    voted = len(answer.upvoted_by.filter(id=user.id)) > 0
    if not voted:
        answer.upvoted_by.add(user)
    else:
        answer.upvoted_by.remove(user)

    context = {
        'answer': {
            'answer': answer,
            'upvotes': len(answer.upvoted_by.all()),
            'voted': not voted
        }
    }
    response_data = {
        'html': render_to_string('objects/forum/upvote_answer.html', RequestContext(request, context)),
        'id_selector': '#upvote_answer_' + str(answer.id)
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")
