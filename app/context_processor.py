
from app.models import *
from app.course_info import *

def user_authenticated(request):
    if request.user and request.user.is_authenticated():
        return request.user.username
    return False

def course_timeline_context(courses):
    context = {}

    categories = MAJOR_TYPES

    courses = sorted(courses, key=lambda x: x.name)

    # Add the courses to the context
    allcourses = []
    for course in courses:
        noSchoolCatalogue = course.catalogue \
            .replace('School of Humanities and Social Sciences', 'SHSS') \
            .replace('School of Engineering and Science', 'SES') \
            .replace('Language Courses', 'Language') \
            .replace('Undergraduate Level Courses', 'UnderGrad') \
            .replace('Graduate Level Courses', 'Grad')

        major = ""
        school = ""
        studies = "UG" if " Undergraduate Level Courses" in course.catalogue else ("Grad" if " Graduate Level Courses" in course.catalogue else "")
        
        ratings = Rating.objects.filter(course= course, rating_type=OVERALL_R)
        if (len(ratings) == 0):
            overall_rating = None
        else:   
            overall_rating = sum([cur.rating for cur in ratings])/len(ratings)

        for m in categories:
            if m[1] in noSchoolCatalogue:
                major = m[0]
                school = m[2]
        allcourses.append({
            'course': course,
            'profs': course.instructors.all(),
            'major': major,
            'school': school,
            'studies': studies,
            'catalogue': noSchoolCatalogue,
            'overall_rating': overall_rating
        })
    allcourses = sorted(allcourses, key=lambda x:x['overall_rating'], reverse=True)
    context['courses'] = allcourses

    context['categories'] = categories

    return context

def course_page_context(request, course):
    context = {}
    context['course'] = course

    course_types = dict(COURSE_TYPES)
    context['course_type'] = course_types[course.course_type]
    context['instructors'] = course.instructors.all()

    context['ratings'] = []
    allratings = Rating.objects.filter(course= course)
    for rating_type in RATING_TYPES:
        ratings = allratings.filter(rating_type=rating_type[0])
        if len(ratings) > 0:
            rating = sum([cur.rating for cur in ratings])/len(ratings)
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
            context['ratings'].append( dict(context_rating.items() + specific_rating.items()) )
        else:
            professors = course.instructors.all()
            for prof in professors:
                profratings = Professor_Rating.objects.filter(course= course, prof=prof)
                if len(profratings) > 0:
                    profrating = sum([cur.rating for cur in profratings])/len(profratings)
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
                context['ratings'].append( dict(context_rating.items() + specific_rating.items()) )


    comments = Comment.objects.filter(course=course)
    context['comments'] = comments

    return context
