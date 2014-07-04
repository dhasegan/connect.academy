from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.forum.views',
    url(r'^course/(?P<slug>[\w-]+)/$', 'forum_course', name='forum_course'),
    url(r'^course/(?P<slug>[\w-]+)/register$', 'forum_course_registration', name='forum_course_registration')
)
