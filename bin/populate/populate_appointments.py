# Parse appointments

from django.utils import timezone
import pytz

# Insert results into the DB

from app.models import *
import json

f = open('bin/combiner/courseDetails')
coursesList = json.load(f)
f.close()
#print len(coursesList)
for courseDetails in coursesList:
    course = jCourse.objects.filter(name=courseDetails["CourseName"])[0]
    if course.appointments.all().count() > 0:
        continue
    if "Appointments" in courseDetails:
        for appointment in courseDetails["Appointments"]:
            start = datetime.now()
            end = datetime.now()
            if "May" in appointment['start']:
                start = datetime.strptime(appointment['start'], "%d. %b %Y %H:%M")
                end = datetime.strptime(appointment['end'], "%d. %b %Y %H:%M")
            else:
                # There's a dot after the month, if it's not May (FUCKING CAMPUSNET)
                start = datetime.strptime(appointment['start'], "%d. %b. %Y %H:%M")
                end = datetime.strptime(appointment['end'], "%d. %b. %Y %H:%M")
            location = appointment['location']
            description = appointment['description']
            aware_start = timezone.make_aware(start, pytz.timezone("Europe/Berlin"))
            aware_end = timezone.make_aware(end, pytz.timezone("Europe/Berlin"))
            utc_start = timezone.localtime(aware_start, pytz.utc)
            utc_end = timezone.localtime(aware_end, pytz.utc)
            course = Course.objects.get(name=courseDetails["CourseName"])
            CourseAppointment.objects.create(start=utc_start, end=utc_end, location=location, 
                                            description=description, course=course) 
