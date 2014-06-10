from django.conf.urls import patterns, url


urlpatterns = patterns('app.profile.views',
    url(r'^profile/(?P<username>[\w\-\.]+)$', 'profile', name='profile'),
    url(r'^manage_account$', 'manage_account', name='manage_account'),
    url(r'^password_change_action$', 'password_change_action', name='password_change_action'),
    url(r'^username_change_action$', 'username_change_action', name='username_change_action'),
    url(r'^name_change_action$', 'name_change_action', name='name_change_action'),
)
