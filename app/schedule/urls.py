from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.schedule.views',
    url(r'^view_schedule$', 'view_schedule', name='view_schedule'),
)