from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.views',
    url(r'^welcome$', 'welcome'),
    url(r'^$', 'welcome'),

    url(r'^home$', 'explore', name='home'),
    url(r'^explore$', 'explore', name='explore'),
    url(r'^dashboard$', 'dashboard', name='dashboard'),

    url(r'^about$', 'about'),
    url(r'^all_comments$', 'all_comments', name='all_comments'),
)

urlpatterns += patterns('',
    url(r'^', include('app.auth.urls')),
    url(r'^', include('app.profile.urls')),
    url(r'^', include('versioning.urls')),
    url(r'^course/(?P<slug>[\w-]+)/', include('app.course.urls')),
    url(r'^admin/', include('app.admin.urls')),
    url(r'^forum/', include('app.forum.urls')),
    url(r'^wiki/(?P<slug>[\w-]+)/',include('app.wiki.urls')),
    url(r'^wiki/(?P<slug>[\w-]+)/',include('versioning.urls')),
    url(r'^', include('app.schedule.urls')),
)


