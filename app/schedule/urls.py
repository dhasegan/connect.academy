from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.schedule.views',
    url(r'^view_schedule$', 'view_schedule', name='view_schedule'),
    url(r'^add_personal_appointment','add_personal_appointment',name='add_personal_appointment'),
    url(r'^add_course_appointment','add_course_appointment',name='add_course_appointment'),
)