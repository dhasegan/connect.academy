from django.template.loader import render_to_string

from app.models import *
from app.course_info import *


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


def course_timeline_context(courses):
    context = {}

    courses = sorted(courses, key=lambda x: x.name)
    # Add the courses to the context
    allcourses = []
    for course in courses:
        
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

        allcourses.append({
            'course': course,
            'instructors': course.instructors.all(),
            'majors': course.majors.all(),
            'category': course.category,
            'university': course.university,
            'studies': studies,
            'overall_rating': overall_rating
        })
    allcourses = sorted(allcourses, key=lambda x:x['overall_rating'], reverse=True)
    context['courses'] = allcourses

    category = course.category
    course_path = category.name
    while (category.parent is not None):
        course_path = "%s > %s" % (category.parent.name, course_path)
        category = category.parent


    context['course_path'] = course_path

    return context


def course_page_context(request, course):
    context = {}
    context['course'] = course

    course_types = dict(COURSE_TYPES)
    # Course type seems to be not working?
    # context['course_type'] = course_types[course.course_type]
    context['instructors'] = course.instructors.all()

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
            professors = course.instructors.all()
            for prof in professors:
                profratings = Professor_Rating.objects.filter(course=course, prof=prof)
                if len(profratings) > 0:
                    profrating = sum([cur.rating for cur in profratings]) / len(profratings)
                else:
                    profrating = None
                specific_rating = {
                    'score': profrating,
                    'count': len(profratings),
                    'prof': prof.name
                }
                if request.user.is_authenticated():
                    users = jUser.objects.filter(id=request.user.id)
                    if len(users) > 0:
                        user = users[0]
                        my_ratings = profratings.filter(user=user)
                        if len(my_ratings) > 0:
                            specific_rating['my_score'] = my_ratings[0].rating
                context['ratings'].append(dict(context_rating.items() + specific_rating.items()))

    comments = Comment.objects.filter(course=course)
    context['comments'] = comments

    return context
