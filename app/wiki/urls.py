from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.wiki.views',
    url(r'^$', 'view_wiki_page', name='view_wiki_page'),
    url(r'^edit_wiki_page$', 'edit_wiki_page', name='edit_wiki_page'),
    url(r'^save_wiki_page$', 'save_wiki_page', name="save_wiki_page"),
    url(r'^revert_wiki_page$', 'revert_wiki_page', name="revert_wiki_page"),
)