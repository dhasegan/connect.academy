from django.conf import settings

from app.models import *
from app.ratings import *


def forum_vote_context(obj, current_user):
    # obj is either post or answer
    context = {}

    all_upvotes = obj.upvoted_by.all()
    nr_upvotes = all_upvotes.count()
    time_diff = pytz.utc.localize(datetime.now()) - obj.datetime
    context['upvotes'] = nr_upvotes
    context['voted'] = len(all_upvotes.filter(id=current_user.id)) > 0
    context['rating'] = forum_post_rating(nr_upvotes, time_diff.total_seconds())

    return context


def forum_child_answer_context(post, answer, current_user):
    context = {
        'answer': answer,
        'child_answers': []
    }
    count = 2
    child_answer = answer
    while True:
        child_answers = child_answer.forumanswer_set.all()
        if not child_answers:
            break
        child_answer = child_answers[0]
        count += 1
    context['children'] = count

    context = dict(context.items() + forum_vote_context(answer, current_user).items())
    return context


def forum_answer_context(post, answer, current_user):
    context = {
        'answer': answer,
        'child_answers': []
    }
    child_answers = ForumAnswer.objects.filter(post=post, parent_answer=answer)
    for child in child_answers:
        context['child_answers'].append(forum_child_answer_context(post, child, current_user))

    context = dict(context.items() + forum_vote_context(answer, current_user).items())
    return context


def forum_post_context(post, current_user):
    answers_context = []
    answers = ForumAnswer.objects.filter(post=post, parent_answer=None)
    for answer in answers:
        answers_context.append(forum_answer_context(post, answer, current_user))
    context = {
        'question': post,
        'answers': answers_context,
    }
    context = dict(context.items() + forum_vote_context(post, current_user).items())
    return context


def forum_context(forum, current_user):
    context_forum = {
        "forum": forum,
        "course": forum.course,
        "user": current_user
    }

    context_forum['posts'] = []
    posts = ForumPost.objects.filter(forum=forum)
    for post in posts:
        context_forum['posts'].append(forum_post_context(post, current_user))

    return context_forum


def forum_discussion_answer_context(answer, current_user):
    context = {
        'answer': answer,
        'child_answers': []
    }

    context = dict(context.items() + forum_vote_context(answer, current_user).items())
    return context


def forum_discussion_post_context(post, answer1, answer2, current_user):
    discussion_answers = [forum_discussion_answer_context(answer1, current_user),
                          forum_discussion_answer_context(answer2, current_user)]
    answer = answer2
    while True:
        child_answers = answer.forumanswer_set.all()
        if not child_answers:
            break
        answer = child_answers[0]
        discussion_answers.append(forum_discussion_answer_context(answer, current_user))

    context = {
        'question': post,
        'answers': discussion_answers,
    }
    context = dict(context.items() + forum_vote_context(post, current_user).items())
    return context


def forum_discussion_context(forum, post, answer, current_user):
    parent_answer = answer.parent_answer
    return {
        'post': forum_discussion_post_context(post, parent_answer, answer, current_user),
        'forum': forum,
        'course': forum.course,
        'discussion_answer_id': answer.id
    }
