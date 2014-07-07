from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.forum.views',
    url(r'^(?P<slug>[\w-]+)/$', 'forum_course', name='forum_course'),
    url(r'^(?P<slug>[\w-]+)/new_post$', 'new_post', name="forum_new_post"),
    url(r'^(?P<slug>[\w-]+)/new_answer$', 'new_answer', name="forum_new_answer"),
    url(r'^reply_form/(?P<answer_id>[0-9]+)$', 'reply_form', name="forum_reply_form"),
    url(r'^(?P<slug>[\w-]+)/register$', 'course_registration', name='forum_course_registration')
)
