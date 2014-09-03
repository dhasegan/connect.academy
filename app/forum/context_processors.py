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
    allowed_tags = forum.get_view_tags(current_user)
    context_forum = {
        "forum": forum,
        "user": current_user
    }
    if forum.forum_type == FORUM_COURSE:
        context_forum["course"] = forum.course

    context_forum['posts'] = []
    tags = []
    posts = ForumPost.objects.filter(forum=forum)
    for post in posts:
        if post.tag.name in [atag.name for atag in allowed_tags] or post.posted_by == current_user:
            context_forum['posts'].append(forum_post_context(post, current_user))
            if post.tag not in tags:
                tags.append( post.tag )
    context_forum['tags'] = sorted(tags, key=lambda x:x.name)

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
    context = {
        'post': forum_discussion_post_context(post, parent_answer, answer, current_user),
        'forum': forum,
        'discussion_answer_id': answer.id
    }
    if forum.forum_type == FORUM_COURSE:
        context['course'] = forum.forumcourse.course
    return context

def forum_stats_context(forum):
    posts = ForumPost.objects.filter(forum=forum)
    answers = []
    for post in posts:
        answers += post.forumanswer_set.all()

    total_upvotes = 0
    anon_posts = 0
    anon_answers = 0
    anon_upvotes = 0

    posters = []
    for post in posts:
        if not post.anonymous and not post.posted_by in posters:
            posters.append(post.posted_by)
        if post.anonymous:
            anon_posts += 1
            anon_upvotes += post.upvoted_by.all().count()
        total_upvotes += post.upvoted_by.all().count()
    for answer in answers:
        if not answer.anonymous and not answer.posted_by in posters:
            posters.append(answer.posted_by)
        if answer.anonymous:
            anon_answers += 1
            anon_upvotes += answer.upvoted_by.all().count()
        total_upvotes += answer.upvoted_by.all().count()

    user_stats = []
    for poster in posters:
        nr_posts = 0
        nr_answers = 0
        nr_upvotes = 0
        for post in posts:
            if not post.anonymous and post.posted_by == poster:
                nr_posts += 1
                nr_upvotes += post.upvoted_by.all().count()
        for answer in answers:
            if not answer.anonymous and answer.posted_by == poster:
                nr_answers += 1
                nr_upvotes += answer.upvoted_by.all().count()

        user_stats.append({
            'student': poster,
            'nr_posts': nr_posts,
            'nr_answers': nr_answers,
            'nr_activity': nr_posts + nr_answers,
            'nr_upvotes': nr_upvotes,
        })

    context = {
        'total_posts': len(posts),
        'total_answers': len(answers),
        'total_upvotes': total_upvotes,
        'anon_posts': anon_posts,
        'anon_answers': anon_answers,
        'anon_upvotes': anon_upvotes,
        'user_stats': user_stats
    }

    tags = list(ForumTag.objects.filter(tag_type=FORUMTAG_PRIMARY))
    tags += list(forum.forumtopictag_set.all())
    tags += list(forum.forumextratag_set.all())

    tags_stats = []
    for tag in tags:
        tags_stats.append({
            'tag': tag,
            'nr_posts': tag.forumpost_set.filter(forum=forum).count()
        })
    context['tags_stats'] = tags_stats


    return context
