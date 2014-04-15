from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.course.views',
    url(r'^course/(?P<slug>[\w-]+)', 'course_page', name='course_page'),
    url(r'^course_image/(?P<slug>[\w-]+)', 'get_course_image', name='course_image'),
    url(r'^submit_comment', 'submit_comment', name='submit_comment'),
    url(r'^rate_course', 'rate_course', name='rate_course'),
)
