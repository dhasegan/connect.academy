from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.manage.views',
	url(r'^$', 'course_categories', name='course_categories'),
	url(r'^course_categories$', 'course_categories', name='course_categories'), 
	url(r'^admin_form_action$', 'admin_form_action', name='admin_form_action'),

)
