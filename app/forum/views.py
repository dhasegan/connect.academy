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
from app.decorators import *


@require_GET
@login_required
def forum_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)

    context = {
        "page": "forum_course",
    }
    context["course"] = course

    forum = course.forum
    context = dict(context.items() + forum_context(forum, user).items())

    if 'filter' in request.GET and request.GET['filter']:
        tag = request.GET['filter']
        if tag in [vtag.name for vtag in forum.get_view_tags(user)]:
            context['current_filter'] = tag

    if 'post' in request.GET and request.GET['post']:
        context['current_post'] = int(request.GET['post'])

    return render(request, "pages/forum/page.html", context)


@require_http_methods(["GET", "POST"])
@require_active_user
@login_required
def new_post(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)
    context = {
        "page": "forum_new_post"
    }
    context["course"] = course
    context['forum'] = course.forum
    post_tags = course.forum.get_post_tags(user)
    context['tags'] = post_tags

    # Get request
    if request.method == "GET":
        return render(request, "pages/forum/new_post.html", context)

    # Post request
    form = SubmitForumPost(request.POST)
    if not form.is_valid():
        raise Http404

    # user permissions to post:
    if form.cleaned_data['tagsRadios'] not in [tag.name for tag in post_tags]:
        raise Http404

    form_tag = None
    for tag in post_tags:
        if tag.name == form.cleaned_data['tagsRadios']:
            form_tag = tag

    post = ForumPost(name=form.cleaned_data['title'], forum=form.cleaned_data['forum'],
                     text=form.cleaned_data['description'], posted_by=user,
                     anonymous=form.cleaned_data['anonymous'], tag=form_tag)
    post.save()
    

    return redirect("app.forum.views.forum_course", slug=course.slug)


@require_POST
@require_active_user
@login_required
def new_answer(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = get_object_or_404(jUser, id=request.user.id)
    context = {}

    context["course"] = course
    forum = course.forum
    answer_tags = forum.get_answer_tags(user)

    form = SubmitForumAnswer(request.POST)
    if not form.is_valid():
        raise Http404

    # user permissions to post:
    tag = form.cleaned_data['post'].tag
    if not tag.name in [atag.name for atag in answer_tags] and \
        form.cleaned_data['post'].posted_by != user:
            raise Http404

    parent_answer = None
    if 'parent_answer' in form.cleaned_data and form.cleaned_data['parent_answer']:
        parent_answer = form.cleaned_data['parent_answer']

    answer = ForumAnswer(text=form.cleaned_data['text'], post=form.cleaned_data['post'],
                         parent_answer=parent_answer, posted_by=user, anonymous=form.cleaned_data['anonymous'])
    answer.save()

    if 'discussion_answer' in form.cleaned_data and form.cleaned_data['discussion_answer']:
        context = forum_discussion_context(forum, form.cleaned_data['post'], form.cleaned_data['discussion_answer'], user)
        template_filename = "objects/forum/discussion.html"
    else:
        context['forum'] = forum
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
    context = {
        'parent_answer': {
            'answer': answer,
            'child_answers': []
        },
        'question': post,
        'forum': post.forum,
        'course': post.forum.course
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
    context = forum_discussion_context(post.forum, post, answer, user)

    response_data = {
        'html': render_to_string("objects/forum/discussion.html", RequestContext(request, context))
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_GET
@login_required
def answers(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    user = get_object_or_404(jUser, id=request.user.id)

    context = {
        'course': post.forum.course,
        'forum': post.forum,
        'post': forum_post_context(post, user)
    }

    response_data = {
        'html': render_to_string("objects/forum/answers.html", RequestContext(request, context))
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_POST
@require_active_user
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
        post.followed_by.add(user)
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
@require_active_user
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
