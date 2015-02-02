import json
import time
from datetime import * #datetime
import pytz
from helpers import *
import random
from dateutil.parser import parse
from dateutil.tz import tzoffset

# https://www.ietf.org/rfc/rfc2445.txt for iCalendar specification
# use this for validation http://icalvalid.cloudapp.net/

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.core.files import *
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.core.context_processors import csrf

from app.models import *
from app.decorators import *
from app.schedule.forms import *
from django.views.decorators.csrf import requires_csrf_token


#date formatting
date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
ical_date_format = "%Y%m%dT%H%M%S%f"

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
    if user.is_professor():
        courses_managed = user.courses_managed.all()

    context['courses'] = courses_managed

    
    courses_enrolled = user.courses_enrolled.all()

    course_appointments = []

    for course in courses_enrolled:
        course_appointments.append(course.appointments.all())

    for course in courses_managed:
        course_appointments.append(course.appointments.all())

    # get user's PersonalAppointments
    personal_appointments = user.appointments.all()
    
    all_appointments = []

    #get client timezone
    local_timezone = timezone.get_current_timezone()


    # course appointments
    for cappointments in course_appointments:
        for appointment in cappointments:
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
    # TODO: fix this ... 
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

    appointment = CourseAppointment.objects.create(start=start_time,\
                                                    end=end_time,\
                                                    location=location,\
                                                    course = course_to_add_appointment,\
                                                    description = description,\
                                                    course_topic= None) # None for now.

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

# only for personal appointments ? no distinction between personal and course (for now)
# Note that the method uses AJAX.
# TODO Timezones and shit.
@require_POST
@require_active_user
@requires_csrf_token
def import_ical(request):
    
    context = {'warnings':''}

    form = CalendarImportForm(request.POST,request.FILES)

    if not form.is_valid():
        context['status'] = -1
        return HttpResponse(json.dumps(context))

    user = get_object_or_404(jUser, id=request.user.id)
    calFile = form.cleaned_data['calFile']
    calendar = None

    #this returns a calendar object if valid, else None
    calendar = validate_ical(calFile.read(),purpose='import')

    if not calendar:
        context['status'] = -2
        return HttpResponse(json.dumps(context))
    
    #the file should be ok ... start creating appointments.
    appointmentsJSON = [] # what will be sent back as HTTPResponse
    for component in calendar.walk():
        data = {}
        if component.name == "VEVENT":
            startComponent = component.get('dtstart')
            start = startComponent.dt
            endComponent = component.get('dtend')
            end = endComponent.dt
            
            # SEE NOTES  
            if not timezone.is_aware(start) \
               and startComponent.params.to_ical() == '':
                local_timezone = timezone.get_current_timezone()
                start = timezone.make_aware(start,local_timezone)
                start = start.astimezone(pytz.utc)
            else:
                try:
                    tzid = startComponent.params['TZID'].to_ical().replace('-','/') # fix this
                    tz = timezone(tzid)
                    # 'start' is still unaware.
                    start = timezone.make_aware(start, tz)
                    start = start.astimezone(pytz.utc)
                except Exception:
                    context['warnings'] += 'TZID information (DTSTART) not supported.\
                                            Defaulting to UTC.\n'

            if not timezone.is_aware(end) \
               and endComponent.params.to_ical() == '':
                local_timezone = timezone.get_current_timezone()
                end = timezone.make_aware(end,local_timezone)
                end = end.astimezone(pytz.utc)
            else:
                try:
                    tzid = endComponent.params['TZID'].to_ical().replace('-','/') # fix this
                    tz = timezone(tzid)
                    # 'end' is still unaware.
                    end = timezone.make_aware(end, tz)
                    end = end.astimezone(pytz.utc)
                except Exception:
                    context['warnings'] += 'TZID information (DTEND) not supported.\
                                            Defaulting to UTC.\n'

            description = component.get('description')
            summary = component.get('summary')
            if not description:
                description = summary
            
            title = component.get('title')
            location = component.get('location')
            if not location:
                location = title
            # the DTSTAMP is not realy relevant
            appointment = PersonalAppointment.objects.create(start=start,\
                                              end=end,\
                                              location=location,
                                              description=description,\
                                              user=user)
            
            data['start'] = format_date(start.strftime(date_format))
            data['end'] = format_date(end.strftime(date_format))
            data['body'] = description
            data['title'] = location
            data['modifiable'] = True
            data['type'] = 'Personal'
            data['id'] = appointment.id
            appointmentsJSON.append(data)

        if component.name == "VTODO":
            pass

        if component.name == "VFREEBUSY":
            pass

        if component.name == "VJOURNAL":
            pass

    context['appointments'] = appointmentsJSON
    context['status'] = 0
    return HttpResponse(json.dumps(context))


def export_as_ical(request):
    
    user = get_object_or_404(jUser, id=request.user.id)
    if user.is_professor():
        user_appointments = Appointment.objects.filter(Q(Q(personalappointment__user=user)\
                                                       |                                \
                                                       Q(courseappointment__course__in=user.courses_managed.all())))
    else:
        user_appointments = Appointment.objects.filter(Q(Q(personalappointment__user=user)\
                                                       |                                \
                                                       Q(courseappointment__course__in=user.courses_enrolled.all())))
    
    # at this point, we have all the user appointments. Start creating ical events
    calendar = Calendar()
    calendar.add('prodid','-//Connect Academy//Schedule Exporter//') # should be probably taken to the settings.py
    calendar.add('version','2.0') # and this too ... 

    for appointment in user_appointments:
        event = Event()
        event['uid'] = appointment.id
        # DO NOT CHANGE TO LOCAL TIME (see Notes below)
        event['dtstamp'] = to_ical_date(datetime.now().strftime(ical_date_format),aware=True)
        event['dtstart'] = to_ical_date(appointment.start.strftime(ical_date_format),aware=True)
        event['dtend'] = to_ical_date(appointment.end.strftime(ical_date_format),aware=True)
        
        event['description'] = appointment.description
        event['title'] = appointment.location
        calendar.add_component(event)

    data = calendar.to_ical()

    if not validate_ical(data):
        return Http404

    export_name = user.username + "_schedule.ics"
    response = HttpResponse(calendar.to_ical(), content_type='application/calendar')
    response['Content-Disposition'] = 'attachment; filename="%s"' % export_name
    return response


# NOTES:
# The ics specification illustrates that timezone information is 'stored' in a couple
# of different ways:
# 1) DTSTART: <somedate>'Z' -> i.e.: with a Z in the end of the date string
# 2) DTSTART;TZID=<sometz>: <somedate>
# 3) BEGIN: VTIMEZONE
#    TZID = <someID>
#       <some specifications>
#    END: VTIMEZONE -> i.e.: with a VTIMEZONE element provided inline, if the timezone
#                      is suspected not to be included in the Olson db.
# 4) DTSTART: <somedate> -> i.e.: without a Z in the end. Denotes the same time in EVERY timezone
# 
# On any schedue export (i.e.: Creating of a new calendar file). By default, 
# everything is exported as UTC date. (We might provide the user with an option
# to export them in their local time.) Upon an import however, shit happens:
# 
# 1) If the date is as in the first case above, we're alright. 
# 2) If it is not as in the first case:
#   a) Check for the TZID property.
#       * if supported , make use of it.
#       * if not, store as UTC and issue a warning
#   b) If it is as in the 3rd case (or making use of VTIMEZONE)
#      we store it as UTC and issue a warning
#   c) If it is as in the 4th case, we make use of the uploader's local time
#