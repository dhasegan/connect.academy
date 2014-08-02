from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.explore.views',
    url(r'^$', 'explore', name='explore'),
    url(r'^categories$', 'explore_categories', name='explore_categories'),
)
