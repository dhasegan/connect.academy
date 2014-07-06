from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.forum.views',
    url(r'^(?P<slug>[\w-]+)/$', 'forum_course', name='forum_course'),
    url(r'^(?P<slug>[\w-]+)/new_post$', 'forum_new_post', name="forum_new_post"),
    url(r'^(?P<slug>[\w-]+)/new_answer$', 'forum_new_answer', name="forum_new_answer"),
    url(r'^(?P<slug>[\w-]+)/register$', 'forum_course_registration', name='forum_course_registration')
)
