from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.auth.views',
    url(r'^login$','login_action', name='login'),
    url(r'^logout$', 'logout_action', name='logout'),
    url(r'^register$', 'signup_action', name='register'),
    url(r'^set_email$', 'set_email', name='set_email'),
    url(r'^resend_confirmation_email$', 'resend_confirmation_email', name='resend_confirmation_email'),
    url(r'^confirmation/(?P<username>[A-Za-z0-9\._-]{3,25})/(?P<confirmation>[A-Za-z0-9\._-]+)$', 'validate_user', name='confirmation'),
    url(r'^delete/(?P<username>[A-Za-z0-9\._-]{3,25})/(?P<confirmation>[A-Za-z0-9\._-]+)$', 'delete_user', name='delete'), # delete user with confirmation_hash
    url(r'^university_by_email\.*$', 'university_by_email', name='university_by_email'),
    url(r'^check_username\.*$', 'check_username', name='check_username'),
    url(r'^validate_registration\.*$', 'validate_registration', name='check_password'),
    
    ## RESET PASSWORD
    url(r'^send_email_pw_reset$', 'send_email_pw_reset', name='send_email_pw_reset'),
    url(r'^password_reset/(?P<username>[A-Za-z0-9\._-]{3,25})/(?P<token>[A-Za-z0-9\._-]+)$', 'password_reset', name='password_reset'),
    url(r'^new_password$', 'new_password', name='new_password'),
)