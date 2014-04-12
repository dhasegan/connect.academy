from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
	url(r'^welcome$', 'app.views.welcome'),
    url(r'^$', 'app.views.welcome'),
	url(r'^home$', 'app.views.home', name='home'),
    url(r'^all_comments$', 'app.views.all_comments', name='all_comments'),
    url(r'^course/(?P<slug>[\w-]+)', 'app.views.course_page', name='course_page'),
    url(r'^course_image/(?P<slug>[\w-]+)', 'app.views.get_course_image', name='course_image'),
    url(r'^submit_comment', 'app.views.submit_comment', name='submit_comment'),
    url(r'^login$','app.views.login_action', name='login'),
    url(r'^logout$', 'app.views.logout_action', name='logout'),
    url(r'^register$', 'app.views.signup_action', name='register'),
    url(r'^rate_course', 'app.views.rate_course', name='rate_course'),
    url(r'^send_confirmation$', 'app.views.send_confirmation', name='send_confirmation'),
    url(r'^confirmation/(?P<username>[\w-]+)/(?P<confirmation>[\w-]+)$', 'app.views.validate_user', name='confirmation'),
    url(r'^delete/(?P<username>[\w-]+)/(?P<confirmation>[\w-]+)$', 'app.views.delete_user', name='delete'), # delete user with confirmation_hash
    url(r'^profile/(?P<username>[\w-]+)$', 'app.views.profile', name='profile'),
    url(r'^manage_account$','app.views.manage_account',name='manage_account'),
    url(r'^password_change_action$','app.views.password_change_action', name='password_change_action'),
    url(r'^username_change_action$','app.views.username_change_action', name='username_change_action'),
    url(r'^name_change_action$','app.views.name_change_action',name='name_change_action')
    
)