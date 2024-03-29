from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.forum.views',
    url(r'^general$', 'forum_general', name='forum_general'),
    url(r'^general/new_post$', 'new_post_general', name='forum_new_post_general'),
    url(r'^(?P<slug>[\w-]+)/$', 'forum_course', name='forum_course'),
    url(r'^(?P<slug>[\w-]+)/new_post$', 'new_post_course', name="forum_new_post_course"),
    url(r'^post/(?P<post_id>[0-9]+)$', 'forum_post', name="forum_post"),

    url(r'^new_post$', 'new_post', name="forum_new_post"),
    url(r'^new_answer$', 'new_answer', name="forum_new_answer"),
    url(r'^answers/(?P<post_id>[0-9]+)$', 'answers', name="forum_answers"),
    url(r'^reply_form/(?P<answer_id>[0-9]+)$', 'reply_form', name="forum_reply_form"),
    url(r'^discussion/(?P<answer_id>[0-9]+)$', 'discussion', name="forum_discussion"),

    url(r'^upvote/post$', 'upvote_post', name="upvote_post"),
    url(r'^upvote/answer$', 'upvote_answer', name="upvote_answer"),
    url(r'^downvote/post$', 'downvote_post', name="downvote_post"),
    url(r'^downvote/answer$', 'downvote_answer', name="downvote_answer"),
    url(r'^post/follow$', 'follow_post', name="follow_post"),
    url(r'^post/unfollow$', 'unfollow_post', name="unfollow_post"),

    url(r'^add_extratag$', 'add_extratag', name="add_extratag"),
)
