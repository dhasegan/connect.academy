from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.wiki.views',
    url(r'^(?P<slug>[\w-]+)/edit_wiki_page$', 'edit_wiki_page', name='edit_wiki_page'),
    url(r'^(?P<slug>[\w-]+)/save_wiki_page$', 'save_wiki_page', name="save_wiki_page"),
    url(r'^(?P<slug>[\w-]+)/revert_wiki_page$', 'revert_wiki_page', name="revert_wiki_page"),
)