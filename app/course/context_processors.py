from django.conf import settings

from app.models import *
from app.ratings import *


def course_ratings_context(course, current_user=None):
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


def review_context(comment, current_user=None):
    context_comment = {
        'comment': comment
    }
    upvotes = comment.upvoted_by.all()
    downvotes = comment.downvoted_by.all()

    if not comment.anonymous:
        context_comment['posted_by'] = comment.posted_by

    nr_upvotes = upvotes.count()
    nr_downvotes = downvotes.count()
    context_comment['upvotes'] = nr_upvotes
    context_comment['downvotes'] = nr_downvotes
    if nr_downvotes > 3:
        context_comment['dont_show'] = True

    if upvotes.filter(id=current_user.id).count() > 0:
        context_comment['upvoted'] = True
    if downvotes.filter(id=current_user.id).count() > 0:
        context_comment['downvoted'] = True

    return context_comment


def course_reviews_context(course, current_user=None):
    context = []
    reviews = course.review_set.all()
    for review in reviews:
        context.append(review_context(review, current_user))
    return context


def course_homework_context(course, current_user):
    current_time = pytz.utc.localize(datetime.now())

    context = []
    all_homework = course.coursehomeworkrequest_set.all()
    for hw in all_homework:
        within_deadline = hw.deadline.start <= current_time and current_time < hw.deadline.end
        is_allowed = course.get_registration_status(current_user) == COURSE_REGISTRATION_REGISTERED
        is_student = current_user in course.students.all()
        can_submit_homework = is_student and is_allowed and within_deadline
        
        homework_submission = None
        homework_submissions = CourseHomeworkSubmission.objects.filter(submitter=current_user, homework_request=hw)
        if homework_submissions:
            homework_submission = homework_submissions[0]

        context.append({
            "homework": hw,
            "can_submit": can_submit_homework,
            "is_allowed": is_allowed,
            "previous_submission": homework_submission
        })
    return context

def course_syllabus_context(course, current_user):
    context = []
    for topic in course.course_topics.all():
        topic_context = {
            'topic': topic,
            'documents': topic.documents.all(),

        }
        if current_user in course.students.all() or current_user in course.professors.all():
            topic_context['homework'] = [hw for hw in course_homework_context(course,current_user) 
                                            if hw['homework'].course_topic == topic]

        context.append(topic_context)
    return context


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
    context['ratings'] = course_ratings_context(course, current_user)
    context['comments'] = course_reviews_context(course, current_user)

    # Course path
    course_path = None
    university_category = course.university.get_university_category()
    category = course.category
    while category is not None and category != university_category:
        course_path = "%s > %s" % (category.name, course_path) if course_path else category.name
        category = category.parent
    context['course_path'] = course_path

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
    context['syllabus'] = course_syllabus_context(course,current_user)

    # Course forum link
    context['forum'] = course.forum

    context['documents'] = course.documents.filter(course_topic=None)

    # Show documents/homework only if the user is registered
    if registration_status == COURSE_REGISTRATION_REGISTERED:
        # context['can_upload_docs'] = user in course.professors.all() <<< TO BE CHANGED    
        context['current_homework'] = [hw for hw in course_homework_context(course, current_user) if hw['is_allowed']]

    return context
