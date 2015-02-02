import json
import time
from datetime import * #datetime
import pytz
from helpers import *
from dateutil.parser import parse
from dateutil.tz import tzoffset

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
from app.decorators import *
from app.schedule.forms import *
from django.views.decorators.csrf import requires_csrf_token


#date formatting
date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

@login_required
def view_schedule(request):
    context = {
        'page': 'view_schedule'
    }

    # get the CourseAppointments of the courses the user is registered in
    
    user = get_object_or_404(jUser, id=request.user.id)

    #needed to find out which of the forms to render.
    context['user'] = user

    courses_managed = []
    courses_managed_list = []
    courses_assisted = []
    if user.is_professor():
        courses_managed = user.courses_managed.all()

    context['courses'] = courses_managed

    student_registrations = StudentCourseRegistration.objects.filter(student=user)
    #courses_enrolled = user.courses_enrolled.all()

    course_appointments = []

    for reg in student_registrations:
        course_appointments += CourseAppointment.objects.filter(
            Q(course_module=None)|Q(course_module=reg.module),
            course = reg.course
            
        )

    for course in courses_managed:
        course_appointments += course.appointments.all()

    for course in user.courses_assisted.all():
        course_appointments += course.appointments.all()

    # get user's PersonalAppointments
    personal_appointments = user.appointments.all()
    
    all_appointments = []

    #get client timezone
    local_timezone = timezone.get_current_timezone()


    # course appointments
    for appointment in course_appointments:

        data = {}
        data['id'] = appointment.id
        
        start_local = timezone.localtime(appointment.start,local_timezone) # the time to display to the user
        end_local = timezone.localtime(appointment.end,local_timezone)   


        data['start'] = format_date(start_local.strftime(date_format))
        data['end'] = format_date(end_local.strftime(date_format))
        
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
        data['courseModule'] = appointment.course_module.name if appointment.course_module else None
        all_appointments.append(data)


    for appointment in personal_appointments:
        data = {}
        data['id'] = appointment.id
        
        start_local = timezone.localtime(appointment.start,local_timezone) 
        end_local = timezone.localtime(appointment.end,local_timezone)   

        data['start'] = format_date(start_local.strftime(date_format))
        data['end'] = format_date(end_local.strftime(date_format))
        
        data['title'] = appointment.location
        data['body'] = appointment.description
        data['modifiable'] = True
        data['type'] = 'Personal'
        
        all_appointments.append(data)

    context['appointments'] = json.dumps(all_appointments)

    return render(request, "pages/schedule/view_schedule.html", context)

#both professors and students
@require_POST
@require_active_user
@requires_csrf_token
def add_personal_appointment(request):
    
    form = PersonalAppointmentForm(request.POST)

    if not form.is_valid():
        raise Http404

    user = jUser.objects.get(username=request.user.username)
    description = form.cleaned_data['body']
    start = form.cleaned_data['start']
    end = form.cleaned_data['end']
    location = form.cleaned_data['title']
    appointment = PersonalAppointment.objects.create(start=start\
                                                    ,end=end \
                                                    ,location=location \
                                                    ,description=description \
                                                    ,user=user)

    # Send the newly created appointment back to the client.
    appointmentsJSON = []
    local_timezone = timezone.get_current_timezone()

    start_local = timezone.localtime(start,local_timezone)
    end_local = timezone.localtime(end,local_timezone)
    data = {}
    data['id'] = appointment.id
    data['start'] = format_date(start_local.strftime(date_format))
    data['end'] = format_date(end_local.strftime(date_format))
    data['title'] = location
    data['body'] = description
    data['modifiable'] = True
    data['type'] = 'Personal'
    
    appointmentsJSON.append(data)

    copy_to_otherweeks = form.cleaned_data['copy']
    weeks = form.cleaned_data['num_weeks']
    
    if copy_to_otherweeks:
        start_times = []
        length = end - start
        for i in range(1,weeks+1):
            start_time = start + timedelta(weeks=i)
            start_times.append(start_time)

        for time in start_times:
            data = {}

            start_local = timezone.localtime(time,local_timezone)
            end_local = timezone.localtime(time+length,local_timezone)   
            
            data['start'] = format_date(start_local.strftime(date_format))
            data['end'] = format_date(end_local.strftime(date_format))

            data['title'] = location
            data['body'] = description
            data['modifiable'] = True
            data['type'] = 'Personal'
            
            appointment = PersonalAppointment.objects.create(start=time,\
                                                            end= time+length,\
                                                            location=location,\
                                                            description = description,\
                                                            user=user)
            data['id'] = appointment.id
            
            appointmentsJSON.append(data)

    return_dict = {'status':'OK','appointments':appointmentsJSON}

    return HttpResponse(json.dumps(return_dict))

@require_POST
@require_active_user
@requires_csrf_token
def edit_personal_appointment(request):

    form = PersonalAppointmentForm(request.POST)

    if not form.is_valid():
        raise Http404

    id_to_edit = form.cleaned_data['eventId']
    new_description = form.cleaned_data['body']
    new_location = form.cleaned_data['title']
    new_start_time = form.cleaned_data['start']
    new_end_time = form.cleaned_data['end']

    appointment = Appointment.objects.filter(id=id_to_edit).get()
    
    appointment.description = new_description
    appointment.location = new_location
    appointment.start = new_start_time
    appointment.end = new_end_time
    appointment.save()


    appointmentsJSON = []
    local_timezone = timezone.get_current_timezone()

    start_local = timezone.localtime(new_start_time,local_timezone)
    end_local = timezone.localtime(new_end_time,local_timezone)
    data = {}
    data['id'] = appointment.id
    data['start'] = format_date(start_local.strftime(date_format))
    data['end'] = format_date(end_local.strftime(date_format))
    data['title'] = new_location
    data['body'] = new_description
    data['modifiable'] = True
    data['type'] = 'Personal'
    
    appointmentsJSON.append(data)


    # return the newly created appointments back to the user
    return_dict = {'status':'OK','appointments':appointmentsJSON}
    return HttpResponse(json.dumps(return_dict))


@require_POST
@require_active_user
@requires_csrf_token
def remove_personal_appointment(request):

    if request.is_ajax():
        id_to_delete = request.POST['id']
        Appointment.objects.filter(id=id_to_delete).delete()
    else:
        raise Http404

    return_dict = {'status':'OK'}    
    return HttpResponse(json.dumps(return_dict))


#only for professors
@require_POST
@require_active_user
@require_professor
@requires_csrf_token
def add_course_appointment(request):
    user = get_object_or_404(jUser, id=request.user.id)
    
    form = CourseAppointmentForm(request.POST)

    if not form.is_valid():
        raise Http404


    # there might be courses with the same name in the db, however, we want the course with that name and also managed by THIS professor
    courses_managed = user.courses_managed.all()
    
    course = form.cleaned_data['course']

    if not course in courses_managed:
        raise Http404


    description = form.cleaned_data['body']
    start_time = form.cleaned_data['start']
    end_time = form.cleaned_data['end']
    location = form.cleaned_data['title']
    copy_to_otherweeks = form.cleaned_data['copy']
    weeks = form.cleaned_data['num_weeks']
    course_to_add_appointment = form.cleaned_data['course']
    course_module = form.cleaned_data.get('module',None)
    appointment = CourseAppointment.objects.create(start=start_time,\
                                                    end=end_time,\
                                                    location=location,\
                                                    course = course_to_add_appointment,\
                                                    description = description,\
                                                    course_topic= None,
                                                    ) # None for now.
    if course_module:
        appointment.course_module = course_module
        appointment.save()

    appointmentsJSON = []
    local_timezone = timezone.get_current_timezone()

    start_local = timezone.localtime(start_time,local_timezone)
    end_local = timezone.localtime(end_time,local_timezone)
    data = {}
    data['id'] = appointment.id
    data['start'] = format_date(start_local.strftime(date_format))
    data['end'] = format_date(end_local.strftime(date_format))
    data['title'] = location
    data['body'] = description
    data['modifiable'] = True
    data['type'] = 'Course'
    data['courseName'] = appointment.course.name
    data['courseModule'] = appointment.course_module.name if appointment.course_module else None
    
    appointmentsJSON.append(data)

    if copy_to_otherweeks:
        start_times = []
        length = end_time - start_time
        for i in range(1,int(weeks)+1):
            start_time_weeks = start_time + timedelta(weeks=i)
            start_times.append(start_time_weeks)

        for time in start_times:
            appointment = CourseAppointment.objects.create(start=time,\
                                                            end= time+length,\
                                                            location=location,\
                                                            course = course_to_add_appointment,\
                                                            description = description,\
                                                            course_topic= None) # None for now.
            if course_module:
                appointment.course_module = course_module
                appointment.save()
            data = {}
            data['id'] = appointment.id

            start_local = timezone.localtime(time,local_timezone)
            end_local = timezone.localtime(time+length,local_timezone)   
            
            data['start'] = format_date(start_local.strftime(date_format))
            data['end'] = format_date(end_local.strftime(date_format))

            data['title'] = location
            data['body'] = description
            data['modifiable'] = True
            data['type'] = 'Course'
            data['courseName'] = appointment.course.name
            data['courseModule'] = course_module.name if course_module else None
            appointmentsJSON.append(data)

    return_dict = {'status':'OK', 'appointments':appointmentsJSON }    
    return HttpResponse(json.dumps(return_dict))    


@require_POST
@require_professor
@require_active_user
@requires_csrf_token
def edit_course_appointment(request):

    form = CourseAppointmentForm(request.POST)

    user = get_object_or_404(jUser, id=request.user.id)
    
    if not form.is_valid():
        raise Http404

    
    id_to_edit = form.cleaned_data['eventId']
    new_description = form.cleaned_data['body']
    new_location = form.cleaned_data['title']
    new_start_time = form.cleaned_data['start']
    new_end_time = form.cleaned_data['end']

    appointment = CourseAppointment.objects.filter(id=id_to_edit).get()
        
    appointment.description = new_description
    appointment.location = new_location
    appointment.start = new_start_time
    appointment.end = new_end_time
    appointment.save()

    appointmentsJSON = []
    local_timezone = timezone.get_current_timezone()

    start_local = timezone.localtime(new_start_time,local_timezone)
    end_local = timezone.localtime(new_end_time,local_timezone)
    data = {}
    data['id'] = appointment.id
    data['start'] = format_date(start_local.strftime(date_format))
    data['end'] = format_date(end_local.strftime(date_format))
    data['title'] = appointment.location
    data['body'] = appointment.description
    data['modifiable'] = True
    data['type'] = 'Course'
    data['courseName'] = appointment.course.name
    data['courseModule'] = appointment.course_module.name if appointment.course_module else None
    appointmentsJSON.append(data)

    return_dict = {'status':'OK','appointments':appointmentsJSON}    
    return HttpResponse(json.dumps(return_dict))

@require_POST
@require_active_user
@require_professor
@requires_csrf_token
def remove_course_appointment(request):

    user = get_object_or_404(jUser, id=request.user.id)
    
    id_to_delete = request.POST['id']
    course = get_object_or_404(Course,name=request.POST['courseName'])
    
    if not user.is_professor_of(course):
        raise Http404

    Appointment.objects.filter(id=id_to_delete).delete()

    return_dict = {'status':'OK'}    
    return HttpResponse(json.dumps(return_dict))

@require_POST
@require_active_user
@requires_csrf_token
def resize_appointment(request):
   
    user = get_object_or_404(jUser, id=request.user.id)

    appointmentType = request.POST['type']

    if appointmentType == "0": #personal
        form = PersonalAppointmentForm(request.POST)

        if not form.is_valid():
            raise Http404

        id_to_edit = form.cleaned_data['eventId']
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
        
        appointment = Appointment.objects.filter(id=id_to_edit).get()

        appointment.start = start_time
        appointment.end = end_time
        appointment.save()

        return_dict = {"status":"OK"}

        return HttpResponse(json.dumps(return_dict))
    
    elif appointmentType == "1": #course
        
        form = CourseAppointmentForm(request.POST)
        
        if not form.is_valid():
            raise Http404
        
        if not user.is_professor_of(form.cleaned_data['course']):
            raise Http404

        id_to_edit = form.cleaned_data['eventId']
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']
    
        appointment = Appointment.objects.filter(id=id_to_edit).get()

        appointment.start = start_time
        appointment.end = end_time
        appointment.save()

        return_dict = {"status":"OK"}

        return HttpResponse(json.dumps(return_dict))

    raise Http404


