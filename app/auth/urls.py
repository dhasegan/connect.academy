from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.auth.views',
    url(r'^login$','login_action', name='login'),
    url(r'^logout$', 'logout_action', name='logout'),
    url(r'^register$', 'signup_action', name='register'),
    url(r'^set_email$', 'set_email', name='set_email'),
    url(r'^resend_confirmation_email$', 'resend_confirmation_email', name='resend_confirmation_email'),
    url(r'^confirmation/(?P<username>[\w-]+)/(?P<confirmation>[\w-]+)$', 'validate_user', name='confirmation'),
    url(r'^delete/(?P<username>[\w-]+)/(?P<confirmation>[\w-]+)$', 'delete_user', name='delete'), # delete user with confirmation_hash
)