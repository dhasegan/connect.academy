from django.conf.urls import patterns, url


urlpatterns = patterns('app.profile.views',
    url(r'^profile/(?P<username>[A-Za-z0-9\._-]{2,25})/$', 'profile', name='profile'),
    url(r'^manage_account$', 'manage_account', name='manage_account'),
    url(r'^profile/(?P<username>[A-Za-z0-9\._-]{2,25})/load_profile_activities$', 'load_profile_activities', name='load_profile_activities'),
    url(r'^profile/(?P<username>[A-Za-z0-9\._-]{2,25})/load_new_profile_activities$', 'load_new_profile_activities', name='load_new_profile_activities'),
    url(r'^edit_profile_summary$', 'edit_summary', name='edit_summary'),
    url(r'^new_profile_picture$', 'new_profile_picture', name='new_profile_picture'),

    url(r'^password_change_action$', 'password_change_action', name='password_change_action'),
    url(r'^username_change_action$', 'username_change_action', name='username_change_action'),
    url(r'^name_change_action$', 'name_change_action', name='name_change_action'),
)
