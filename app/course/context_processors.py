from django.conf import settings

from app.models import *
from app.ratings import *


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

    credits = []
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
        categories = categories[::-1]  # reversed

        professors = [pcr.professor for pcr in course.professorcourseregistration_set.filter(is_approved=True)]

        registration_status = course.get_registration_status(user)
        registration = course.get_registration_deadline()
        registration_open = registration.is_open() if registration is not None else False

        if course.credits not in credits:
            credits.append(course.credits)

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
    context['explore_categories'] = explore_categories_context([uni_category.id])

    context['credits'] = sorted(credits)
    return context


def course_ratings_context(request, course, current_user=None):
    context = []
    allratings = course.rating_set.all()

    # All rating types
    for rating_type in RATING_TYPES:
        ratings = allratings.filter(rating_type=rating_type[0])

        rating = None
        if len(ratings) > 0:
            rating = sum([cur.rating for cur in ratings]) / len(ratings)
        # Add the general ratings
        context_rating = {
            'type': rating_type[1],
            'type_db': rating_type[0],
        }
        specific_rating = {
            'score': rating,
            'count': len(ratings)
        }
        if current_user:
            my_ratings = ratings.filter(user=current_user)
            if my_ratings:
                specific_rating['my_score'] = my_ratings[0].rating

        if rating_type[0] == PROFESSOR_R:
            professors = course.professors.all()
            for prof in professors:
                profratings = ratings.filter(professor=prof)
                profrating = None
                if profratings:
                    profrating = sum([cur.rating for cur in profratings]) / len(profratings)
                specific_rating = {
                    'score': profrating,
                    'count': len(profratings),
                    'professor': prof,
                }
                if current_user:
                    my_ratings = profratings.filter(user=current_user)
                    if my_ratings:
                        specific_rating['my_score'] = my_ratings[0].rating
                context.append(dict(context_rating.items() + specific_rating.items()))
        else:
            context.append(dict(context_rating.items() + specific_rating.items()))
    return context


def review_context(request, comment, current_user=None):
    context_comment = {
        'comment': comment
    }
    upvotes = comment.upvoted_by.all()
    downvotes = comment.downvoted_by.all()

    nr_upvotes = upvotes.count()
    nr_downvotes = downvotes.count()
    # Add a +1 to nr_upvotes to fix the ratings score
    context_comment['rating'] = comment_rating(nr_upvotes + 1, nr_downvotes)
    if nr_upvotes + nr_downvotes > 0:
        context_comment['score'] = str(nr_upvotes) + "/" + str(nr_upvotes + nr_downvotes)
    if (nr_upvotes + 1) * 2 < nr_downvotes:
        context_comment['dont_show'] = True

    if not comment.anonymous:
        context_comment['posted_by'] = comment.posted_by

    already_voted = False
    if current_user:
        users_votes = upvotes.filter(id=current_user.id).count() + \
            downvotes.filter(id=current_user.id).count()
        if users_votes:
            already_voted = True
    context_comment['should_vote'] = not already_voted

    return context_comment


def course_reviews_context(request, course, current_user=None):
    context = []
    reviews = course.review_set.all()
    for review in reviews:
        context.append(review_context(request, review, current_user))
    return context


def course_homework_context(request, course, current_user):
    current_time = pytz.utc.localize(datetime.now())

    context = []
    all_homework = course.coursehomeworkrequest_set.all()
    for hw in all_homework:
        can_submit_homework = False
        if hw.deadline.start < current_time and current_time < hw.deadline.end:
            can_submit_homework = True
        homework_submission = None
        homework_submissions = CourseHomeworkSubmission.objects.filter(submitter=current_user, homework_request=hw)
        if homework_submissions:
            homework_submission = homework_submissions[0]

        context.append({
            "homework": hw,
            "can_submit": can_submit_homework,
            "previous_submission": homework_submission
        })


def course_page_context(request, course):
    context = {}
    context['course'] = course

    course_types = dict(COURSE_TYPES)
    # Course type seems to be not working?
    # context['course_type'] = course_types[course.course_type]
    context['professors'] = course.professors.all()

    # Current user
    current_user = None
    if request.user.is_authenticated():
        current_user = jUser.objects.get(id=request.user.id)

    # Ratings and comments
    context['ratings'] = course_ratings_context(request, course, current_user)
    context['comments'] = course_reviews_context(request, course, current_user)

    # User - Course Registration status (open|pending|registered|not allowed)
    registration_status = course.get_registration_status(request.user)
    registration_deadline = course.get_registration_deadline()  # course registration deadline

    # Is course registration open?
    registration_open = False
    if registration_deadline is not None:
        registration_open = registration_deadline.is_open()

    context['registration_status'] = registration_status
    context['registration_open'] = registration_open

    # Course syllabus
    context['syllabus'] = list(course.course_topics.all())

    # Course forum link
    context['forum'] = None
    forums = course.forumcourse_set.all()
    if forums.count() == 1:
        context['forum'] = forums[0]

    # Show documents/homework only if the user is registered
    if registration_status == COURSE_REGISTRATION_REGISTERED:
        # context['can_upload_docs'] = user in course.professors.all() <<< TO BE CHANGED
        context['documents'] = course.coursedocument_set.all()
        context['homework'] = course_homework_context(request, course, current_user)

    return context
