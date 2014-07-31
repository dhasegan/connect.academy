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

def student_dashboard_context(request, user):
    context = {
        'courses': []
    }

    registrations = StudentCourseRegistration.objects.filter(student=user)
    for reg in registrations:
        context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved})
    return context

def professor_dashboard_context(request, user):
    context = {
        'courses': []
    }

    registrations = ProfessorCourseRegistration.objects.filter(professor=user)
    for prof_reg in registrations:  # for each professor registration
        course_dict = {'course': prof_reg.course,
                       'is_approved': prof_reg.is_approved}
        if prof_reg.is_approved:
            course_dict['students'] = {'registered': [], 'pending': []}
            # for each student registration
            for student_reg in StudentCourseRegistration.objects.filter(course=prof_reg.course):
                if student_reg.is_approved:
                    course_dict['students']['registered'].append(student_reg.student)
                else:
                    course_dict['students']['pending'].append(student_reg.student)
            course_dict['documents'] = prof_reg.course.coursedocument_set.all()
            course_dict['homework'] = prof_reg.course.coursehomeworkrequest_set.all()
            course_dict['forum'] = None
            forums = prof_reg.course.forumcourse_set.all()
            if forums.count() == 1:
                course_dict['forum'] = forums[0]
        context['courses'].append(course_dict)

    return context

def dashboard_context(request):
    user = jUser.objects.get(id=request.user.id)

    if user.user_type == USER_TYPE_STUDENT:
        return student_dashboard_context(request, user)
    elif user.user_type == USER_TYPE_PROFESSOR:
        return professor_dashboard_context(request, user)

    return {}