import json
import time
import datetime
import pytz
from helpers import *

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

from app.models import *

@login_required
def view_schedule(request):
    context = {
        'page': 'view_schedule'
    }

    # get the CourseAppointments of the courses the user is registered in
    user = get_object_or_404(jUser, id=request.user.id)
    courses_enrolled = user.courses_enrolled.all()

    course_appointments = []

    for course in courses_enrolled:
        course_appointments.append(course.appointments.all())

    # get user's PersonalAppointments
    personal_appointments = user.appointments.all()

    # list of JSON strings
    all_appointments = []

    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    # course appointments
    for cappointments in course_appointments:
        for appointment in cappointments:
            data = {}
            data['id'] = appointment.id
            data['start'] = format_date(appointment.start.strftime(date_format))
            data['end'] = format_date(appointment.end.strftime(date_format))
            if appointment.course_topic.name:
            	data['title'] = appointment.course_topic.name 
            else:
            	data['title']= appointment.description
            
            all_appointments.append(data)

    for appointment in personal_appointments:
        data = {}
        data['id'] = appointment.id
        data['start'] = format_date(appointment.start.strftime(date_format))
        data['end'] = format_date(appointment.end.strftime(date_format))
        data['title'] = appointment.description
        all_appointments.append(data)

    context['appointments'] = json.dumps(all_appointments)

    return render(request, "pages/schedule/view_schedule.html", context)

#both professors and students
@require_POST
def add_personal_appointment(request):
	context = {
		'page':'add_personal_appointment'
	}
	return redirect('/')

@require_POST
def remove_personal_appointment(request):
	context = {
		'page':'remove_personal_appointment'
	}
	return redirect('/')



#only for professors assigned to the course
@require_POST
def add_course_appointment(request):
	context = {
		'page':'add_personal_appointment'
	}
	return redirect('/')

@require_POST
def remove_course_appointment(request):
	context = {
		'page':'remove_course_appointment'
	}
	return redirect('/')
