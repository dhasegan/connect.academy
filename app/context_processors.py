from django.template.loader import render_to_string

from app.models import *
from app.ratings import *

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



def course_timeline_context(courses,user):
    context = {}

    courses = sorted(courses, key=lambda x: x.name)
    # Add the courses to the context
    allcourses = []
    for course in courses:
        if course.category is None:
            continue
        studies = ""
        if course.course_type == COURSE_TYPE_UG:
            studies = "UG"
        elif course.course_type == COURSE_TYPE_GRAD:
            studies = "GRAD"
        
        ratings = Rating.objects.filter(course= course, rating_type=OVERALL_R)
        if (len(ratings) == 0):
            overall_rating = None
        else:   
            overall_rating = sum([cur.rating for cur in ratings])/len(ratings)

        category = course.category
        course_path = category.name
        while (category.parent is not None):
            course_path = "%s > %s" % (category.parent.name, course_path)
            category = category.parent

              
        registration_status = course.get_registration_status(user)

        allcourses.append({
            'course': course,
            'professors': course.professors.all(),
            'majors': course.majors.all(),
            'category': course.category,
            'course_path': course_path,
            'university': course.university,
            'studies': studies,
            'overall_rating': overall_rating,
            'registration_status': registration_status
        })
    allcourses = sorted(allcourses, key=lambda x:x['overall_rating'], reverse=True)
    context['courses'] = allcourses

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
        context['comments'].append( review_context(comment, request, current_user) )


    ### CHECK IF REGISTRATION IS OPEN
    registration_status = OPEN 

    cat = course.category
    registration = cat.get_cr_deadline()
    if registration is None or not registration.is_open():
        registration_status = CLOSED
    elif course.university != user.university or\
           user.user_type != USER_TYPE_STUDENT or\
            not user.is_active:
        registration_status = INVALID
    else:
        registrations = StudentCourseRegistration.objects.filter(student=user,course=course)
        if registrations:
            reg = registrations[0]
            if reg.is_approved:
                registration_status = REGISTERED
            else:
                registration_status = PENDING

    context['registration_status'] = registration_status

    current_time = pytz.utc.localize(datetime.now())

    # Show documents and homework only if the user is registered or pending registration
    if registration_status == REGISTERED or registration_status == PENDING:
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


    return context

def review_context(comment, request, current_user):
    context_comment = {
        'comment': comment
    }

    upvotes = comment.upvoted_by.all().count()
    downvotes = comment.downvoted_by.all().count()
    # Add a +1 to upvotes to fix the ratings score
    context_comment['rating'] = comment_rating(upvotes+1, downvotes)
    if upvotes + downvotes > 0:
        context_comment['score'] = str(upvotes) + "/" + str(upvotes + downvotes)
    if (upvotes + 1) * 2 < downvotes:
        print "dont show"
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

def forum_context(forum, current_user):
    context_forum = {
        "forum": forum,
        "course": forum.course,
        "user": current_user
    }

    context_forum['posts'] = []
    posts = ForumPost.objects.filter(forum=forum)
    for post in posts:
        context_forum['posts'].append({
            'question': post,
            'answers': ForumAnswer.objects.filter(post=post, parent_answer=None)
        })

    return context_forum