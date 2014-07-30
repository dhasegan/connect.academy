from django.template.loader import render_to_string
from django.conf import settings

from app.models import *
from app.ratings import *


def debug(context):
    return {
        'DEBUG': settings.DEBUG
    }


def user_authenticated(request):
    context = {}
    if request.user and request.user.is_authenticated():
        user = request.user
        context["user_auth"] = user
        if not user.is_active:
            if not user.email or user.email == "":
                context['warning'] = render_to_string('objects/notifications/auth/email_not_set.html', {})
            else:
                context['warning'] = render_to_string('objects/notifications/auth/email_not_activated.html', {})

    return context

def explore_level_context(parents, checked=[]):
    context = []

    for parent in parents:
        categories = []
        none_checked = True
        for category in parent.children.all():
            if category.id in checked:
                none_checked = False
            categories.append({
                'category': category,
                'checked': category.id in checked
            })
        if len(categories) > 1:
            context.append({
                'categories': categories,
                'parent': parent,
                'name': parent.name,
                'none_checked': none_checked
            })
    return context

def explore_categories_context(checked=[]):
    context = []

    connect = Category.objects.get(parent=None)
    categories = [connect]
    while categories:
        context.append({
            'level': 0,
            'checkbox_groups': explore_level_context(categories, checked)
        })
        children_categories = []
        for category in categories:
            children = category.children.all()
            if len(children) > 1:
                for child in children:
                    if child.id in checked:
                        children_categories.append( child )
            elif len(children) == 1:
                children_categories.append( children[0] )
        categories = children_categories
    return context


def course_timeline_context(courses, user):
    context = {}

    courses = sorted(courses, key=lambda x: x.name)

    allcourses = []
    for course in courses:
        if course.category is None:
            continue

        categories = []
        category = course.category
        course_path = None
        while category.parent is not None:
            categories.append(category)
            course_path = "%s > %s" % (category.name, course_path) if course_path else category.name
            category = category.parent
        categories = categories[::-1] # reversed

        professors = [pcr.professor for pcr in course.professorcourseregistration_set.filter(is_approved=True)]

        registration_status = course.get_registration_status(user)
        registration = course.get_registration_deadline()
        registration_open = registration.is_open() if registration is not None else False

        allcourses.append({
            'course': course,
            'professors': professors,
            # 'majors': course.majors.all(), # Majors not used yet
            'categories': categories,
            'course_path': course_path,
            'overall_rating': course.get_rating(OVERALL_R),
            'registration_status': registration_status,
            'registration_open': registration_open
        })
    context['courses'] = sorted(allcourses, key=lambda x: x['overall_rating'], reverse=True)

    uni_category = user.university.get_university_category()
    context['explore_categories'] = explore_categories_context([ uni_category.id ])
    return context


def course_page_context(request, course):
    context = {}
    context['course'] = course

    course_types = dict(COURSE_TYPES)
    # Course type seems to be not working?
    # context['course_type'] = course_types[course.course_type]
    context['professors'] = course.professors.all()

    context['ratings'] = []
    allratings = Rating.objects.filter(course=course)
    for rating_type in RATING_TYPES:
        ratings = allratings.filter(rating_type=rating_type[0])
        if len(ratings) > 0:
            rating = sum([cur.rating for cur in ratings]) / len(ratings)
        else:
            rating = None
        context_rating = {
            'type': rating_type[1],
            'type_db': rating_type[0],
        }
        specific_rating = {
            'score': rating,
            'count': len(ratings)
        }
        if request.user.is_authenticated():
            users = jUser.objects.filter(id=request.user.id)
            if len(users) > 0:
                user = users[0]
                my_ratings = ratings.filter(user=user)
                if len(my_ratings) > 0:
                    specific_rating['my_score'] = my_ratings[0].rating
        if rating_type[1] != 'Professor':
            context['ratings'].append(dict(context_rating.items() + specific_rating.items()))
        else:
            professors = course.professors.all()
            for prof in professors:
                profratings = Rating.objects.filter(course=course, professor=prof)
                if len(profratings) > 0:
                    profrating = sum([cur.rating for cur in profratings]) / len(profratings)
                else:
                    profrating = None
                specific_rating = {
                    'score': profrating,
                    'count': len(profratings),
                    'professor': prof,
                }
                if request.user.is_authenticated():
                    users = jUser.objects.filter(id=request.user.id)
                    if len(users) > 0:
                        user = users[0]
                        my_ratings = profratings.filter(user=user)
                        if len(my_ratings) > 0:
                            specific_rating['my_score'] = my_ratings[0].rating
                context['ratings'].append(dict(context_rating.items() + specific_rating.items()))

    current_user = None
    if request.user.is_authenticated():
        current_user = jUser.objects.get(id=request.user.id)

    comments = Review.objects.filter(course=course)
    context['comments'] = []
    for comment in comments:
        context['comments'].append(review_context(comment, request, current_user))

    # User - Course Registration status (open|pending|registered|not allowed)
    registration_status = course.get_registration_status(request.user)
    registration_deadline = course.get_registration_deadline()  # course registration deadline

    # Is course registration open?
    registration_open = False
    if registration_deadline is not None:
        registration_open = registration_deadline.is_open()

    context['registration_status'] = registration_status
    context['registration_open'] = registration_open

    current_time = pytz.utc.localize(datetime.now())

    # Show documents and homework only if the user is registered
    if registration_status == COURSE_REGISTRATION_REGISTERED:
        # context['can_upload_docs'] = user in course.professors.all() <<< TO BE CHANGED
        user = jUser.objects.filter(id=request.user.id)[0]

        context['documents'] = course.coursedocument_set.all()

        context['homework'] = []
        all_homework = course.coursehomeworkrequest_set.all()
        for hw in all_homework:
            can_submit_homework = False
            if hw.deadline.start < current_time and current_time < hw.deadline.end:
                can_submit_homework = True
            homework_submission = None
            homework_submissions = CourseHomeworkSubmission.objects.filter(submitter=user, homework_request=hw)
            if homework_submissions:
                homework_submission = homework_submissions[0]

            context['homework'].append({
                "homework": hw,
                "can_submit": can_submit_homework,
                "previous_submission": homework_submission
            })

        context['forum'] = None
        forums = course.forumcourse_set.all()
        if forums.count() == 1:
            context['forum'] = forums[0]


    # course syllabus
    context['syllabus'] = list(course.course_topics.all())

    return context


def review_context(comment, request, current_user):
    context_comment = {
        'comment': comment
    }

    upvotes = comment.upvoted_by.all().count()
    downvotes = comment.downvoted_by.all().count()
    # Add a +1 to upvotes to fix the ratings score
    context_comment['rating'] = comment_rating(upvotes + 1, downvotes)
    if upvotes + downvotes > 0:
        context_comment['score'] = str(upvotes) + "/" + str(upvotes + downvotes)
    if (upvotes + 1) * 2 < downvotes:
        context_comment['dont_show'] = True

    already_voted = False
    if current_user:
        users_votes = comment.upvoted_by.filter(id=current_user.id).count() + \
            comment.downvoted_by.filter(id=current_user.id).count()
        if users_votes:
            already_voted = True
    context_comment['should_vote'] = not already_voted

    if not comment.anonymous:
        context_comment['posted_by'] = comment.posted_by

    return context_comment

# Forum Contexts ######################


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
