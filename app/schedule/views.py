import json
import time
from datetime import * #datetime
import pytz
from helpers import *
from dateutil.parser import parse
from dateutil.tz import tzoffset
from django.utils.timezone import utc

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.core.context_processors import csrf

from app.models import *

#date formatting
date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

@login_required
def view_schedule(request):
    context = {
        'page': 'view_schedule'
    }

    # get the CourseAppointments of the courses the user is registered in
    
    # need to fix this too 
    user = get_object_or_404(jUser, id=request.user.id)

    #needed to find out which of the forms to render.
    context['user'] = user

    courses_managed = []
    courses_managed_list = []
    if user.is_professor():
        courses_managed = user.courses_managed.all()
        for course in courses_managed:
            courses_managed_list.append(str(course.name))
    
    context['courses_managed'] = courses_managed_list

    
    courses_enrolled = user.courses_enrolled.all()

    course_appointments = []

    for course in courses_enrolled:
        course_appointments.append(course.appointments.all())

    for course in courses_managed:
        course_appointments.append(course.appointments.all())

    # get user's PersonalAppointments
    personal_appointments = user.appointments.all()
    
    all_appointments = []

    # course appointments
    for cappointments in course_appointments:
        for appointment in cappointments:
            data = {}
            data['id'] = appointment.id
            data['start'] = format_date(appointment.start.strftime(date_format))
            data['end'] = format_date(appointment.end.strftime(date_format))
            if appointment.course_topic:
            	data['title'] = appointment.course_topic.name 
            else:
            	data['title']= appointment.location

            data['body'] = appointment.description
            
            if user.is_professor_of(appointment.course):
                data['modifiable'] = True
            else:
                data['modifiable'] = False
            
            data['type'] = 'Course'
            data['courseName'] = appointment.course.name

            all_appointments.append(data)

    for appointment in personal_appointments:
        data = {}
        data['id'] = appointment.id
        data['start'] = format_date(appointment.start.strftime(date_format))
        data['end'] = format_date(appointment.end.strftime(date_format))
        data['title'] = appointment.location
        data['body'] = appointment.description
        data['modifiable'] = True
        data['type'] = 'Personal'
        
        all_appointments.append(data)

    context['appointments'] = json.dumps(all_appointments)

    #need the largest id in the Appointment table.
    latest_id = 0
    try:
        latest_id = Appointment.objects.latest('id').id
    except Exception:
        pass

    context['latest_id'] = latest_id

    return render(request, "pages/schedule/view_schedule.html", context)


#both professors and students
@require_POST
def add_personal_appointment(request):
    context = {
        'page':'add_personal_appointment'
    }
    context.update(csrf(request))

    if request.is_ajax():
        user = jUser.objects.filter(username=request.user.username).get()
        description = request.POST['body']
        start_time = request.POST['start']
        end_time = request.POST['end']
        location = request.POST['title']
        
        start = parse(start_time) # from dateutil.parser
        end = parse(end_time)

        local_timezone = timezone.get_current_timezone() # the current client timezone

        if timezone.is_naive(start):
            start = timezone.make_aware(start,local_timezone)
        if timezone.is_naive(end):
            end = timezone.make_aware(end,local_timezone)

        start_utc = timezone.localtime(start,pytz.utc)
        end_utc = timezone.localtime(end,pytz.utc)   



        appointment = PersonalAppointment(start=start_utc\
                                         ,end=end_utc \
                                         ,location=location \
                                         ,description=description \
                                         ,user=user)
        appointment.save()
    else:
        raise Http404

    return HttpResponse("")

@require_POST
def edit_personal_appointment(request):
    context = {
        'page':'edit_personal_appointment'
    }
    context.update(csrf(request))
    
    if request.is_ajax():
        id_to_edit = request.POST['id']
        new_description = request.POST['body']
        new_location = request.POST['title']
        new_start_time = request.POST['start']
        new_end_time = request.POST['end']

        start = parse(new_start_time)
        end = parse(new_end_time)
        
        local_timezone = timezone.get_current_timezone()

        if timezone.is_naive(start):
            start = timezone.make_aware(start,local_timezone)
        if timezone.is_naive(end):
            end = timezone.make_aware(end,local_timezone)

        start_utc = timezone.localtime(start,pytz.utc)
        end_utc = timezone.localtime(end,pytz.utc)

        appointment = Appointment.objects.filter(id=id_to_edit).get()
        
        appointment.description = new_description
        appointment.location = new_location
        appointment.start = start_utc
        appointment.end = end_utc
        appointment.save()
    else:
        raise Http404

    return HttpResponse("")


@require_POST
def remove_personal_appointment(request):
    context = {
        'page':'remove_personal_appointment'
    }
    context.update(csrf(request))

    if request.is_ajax():
        id_to_delete = request.POST['id']
        Appointment.objects.filter(id=id_to_delete).delete()
    else:
        raise Http404

    return HttpResponse("")

#only for professors
@require_POST
def add_course_appointment(request):
    context = {
        'page':'add_course_appointment'
    }
    
    context.update(csrf(request))
    
    user = get_object_or_404(jUser, id=request.user.id)

    if not user.is_professor() or not request.is_ajax():
        raise Http404

    course_name = request.POST['courseName']

    # there might be courses with the same name in the db, however, we want the course with that name and also managed by THIS professor
    courses_managed = user.courses_managed.all()
    course_to_add_appointment = None
    for course in courses_managed:
        if course_name == course.name:
            course_to_add_appointment = course
            break

    #We have the course

    description = request.POST['body']
    start_time = request.POST['start']
    end_time = request.POST['end']
    location = request.POST['title']
    copy_to_otherweeks = request.POST['copy']

    start = parse(start_time) # from dateutil.parser
    end = parse(end_time)

    local_timezone = timezone.get_current_timezone() # the current client timezone

    if timezone.is_naive(start):
        start = timezone.make_aware(start,local_timezone)
    if timezone.is_naive(end):
        end = timezone.make_aware(end,local_timezone)

    start_utc = timezone.localtime(start,pytz.utc)
    end_utc = timezone.localtime(end,pytz.utc)   

    appointment = CourseAppointment(start=start_utc,\
                                    end=end_utc,\
                                    location=location,\
                                    course = course_to_add_appointment,\
                                    description = description,\
                                    course_topic= None) # None for now.

    appointment.save()

    
    # This needs to be done using some module/package that handles holidays and whatnot.
    # The way it is now is very slow, mainly because of the 364 times the database is accessed
    if copy_to_otherweeks == 'true' : # ugly, I know
        start_times = []
        length = end_utc - start_utc
        for i in range(1,365):
            start_time = start_utc + timedelta(weeks=i)
            if start_time.strftime("%A") == 'Saturday' or start_time.strftime("%A") == 'Sunday': # need to take care of holidays too
                pass
            else:
                start_times.append(start_time)

        for time in start_times:
            appointment = CourseAppointment(start=time,\
                                    end= time+length,\
                                    location=location,\
                                    course = course_to_add_appointment,\
                                    description = description,\
                                    course_topic= None) # None for now.
            appointment.save()
            
    return HttpResponse("")    


@require_POST
def edit_course_appointment(request):
    context ={
        'page':'edit_course_appointment',
    }

    context.update(csrf(request))

    user = get_object_or_404(jUser, id=request.user.id)
    course = get_object_or_404(Course,name=request.POST['courseName'])
    if not user.is_professor_of(course) or not request.is_ajax():
        raise Http404

    id_to_edit = request.POST['id']
    new_description = request.POST['body']
    new_location = request.POST['title']
    new_start_time = request.POST['start']
    new_end_time = request.POST['end']

    start = parse(new_start_time)
    end = parse(new_end_time)
        
    local_timezone = timezone.get_current_timezone()

    if timezone.is_naive(start):
        start = timezone.make_aware(start,local_timezone)
    if timezone.is_naive(end):
        end = timezone.make_aware(end,local_timezone)
    
    start_utc = timezone.localtime(start,pytz.utc)
    end_utc = timezone.localtime(end,pytz.utc)

    appointment = Appointment.objects.filter(id=id_to_edit).get()
        
    appointment.description = new_description
    appointment.location = new_location
    appointment.start = start_utc
    appointment.end = end_utc
    appointment.save()
    
    return HttpResponse("")

@require_POST
def remove_course_appointment(request):
    context = {
        'page':'remove_personal_appointment'
    }
    context.update(csrf(request))

    user = get_object_or_404(jUser, id=request.user.id)
    
    if request.is_ajax() and user.is_professor():
        id_to_delete = request.POST['id']
        course = get_object_or_404(Course,name=request.POST['courseName'])
        
        if not user.is_professor_of(course):
            raise Http404

        Appointment.objects.filter(id=id_to_delete).delete()
    else:
        raise Http404

    return HttpResponse("")

