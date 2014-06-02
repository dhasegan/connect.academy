from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.views',
    url(r'^welcome$', 'welcome'),
    url(r'^$', 'welcome'),
    url(r'^home$', 'home', name='home'),
    url(r'^about$', 'about'),
    url(r'^all_comments$', 'all_comments', name='all_comments'),
    url(r'^university_by_email\.*$', 'university_by_email', name='university_by_email'),
    url(r'^check_username\.*$', 'check_username', name='check_username'),
    url(r'^validate_registration\.*$', 'validate_registration', name='check_password'),

)

urlpatterns += patterns('',
    url(r'^', include('app.auth.urls')),
    url(r'^', include('app.profile.urls')),
    url(r'^course/(?P<slug>[\w-]+)/', include('app.course.urls')),
)
