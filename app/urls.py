from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.views',
    url(r'^welcome$', 'welcome'),
    url(r'^$', 'welcome'),

    url(r'^home$', 'dashboard', name='home'),
    url(r'^dashboard$', 'dashboard', name='dashboard'),
    url(r'^all_comments$', 'all_comments', name='all_comments'),
    url(r'^conduct_code$', 'conduct_code', name='conduct_code'),
    url(r'^load_dashboard_activities$', 'load_dashboard_activities', name='load_dashboard_activities'),
    url(r'^load_new_dashboard_activities$', 'load_new_dashboard_activities', name='load_new_dashboard_activities'),
    url(r'^error/(?P<error_type>[\w-]+)', 'error_page', name="error_page"),
    url(r'^set_timezone$', 'set_timezone', name='set_timezone')
)

urlpatterns += patterns('',
    url(r'^', include('app.auth.urls')),
    url(r'^', include('app.profile.urls')),
    url(r'^', include('versioning.urls')),
    url(r'^course/(?P<slug>[\w-]+)/', include('app.course.urls')),
    url(r'^manage/', include('app.manage.urls')),
    url(r'^forum/', include('app.forum.urls')),
    url(r'^explore/', include('app.explore.urls')),
    url(r'^wiki/(?P<slug>[\w-]+)/',include('app.wiki.urls')),
    url(r'^wiki/(?P<slug>[\w-]+)/',include('versioning.urls')),
    url(r'^', include('app.schedule.urls')),
)
