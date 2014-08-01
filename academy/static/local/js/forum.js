var s,
ForumPage = {
    settings: {
        // Filters
        postFilters: $('.post-filter'),
        currentPostFilter: $('.current-post-filter'),
        postFilterNameSelector: '.post-filter-name',

        // Posts sidebar
        posts: $('.forum-post'),

        // Answers tabs
        postAnswerFormSelector: '.forumpostnewanswer-form',
        getReplyLinkSelector: '.getreplyform-link',
        discussionLinkSelector: '.discussion-link',
        bestanswersLinkSelector: '.bestanswers-link',
        upvotePostFormSelector: '.upvote-post-form',
        upvoteAnswerFormSelector: '.upvote-answer-form',
    },

    init: function() {
        s = this.settings;

        // Index the posts based on the filters
        this.indexPosts();

        // Bind ui actions for answers tab
        this.onRefreshAnswerTab($('html'));
        this.bindUIActions();
    },

    bindUIActions: function() {

        // On Filter change
        s.postFilters.click( function() {
            s.postFilters.removeClass("hidden");
            $(this).addClass("hidden");
            s.currentPostFilter.find(s.postFilterNameSelector).text(this.text);

            ForumPage.indexPosts();
        });
    },

    indexPosts: function() {
        var tag_filter = s.currentPostFilter.find(s.postFilterNameSelector).text().replace("#", "");

        if (tag_filter == "all") {
            s.posts.show()
            return ;
        } 

        s.posts.each( function() {
            var show = $(this).hasClass('ptag-' + tag_filter)

            if (show) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });

        var active_post = s.posts.filter( function() { return $(this).hasClass('active') });
        if (active_post.is(':visible') == false) {
            $visible_posts = s.posts.filter(':visible');
            $visible_posts.first().find('a').click();
        }
    },

    // Refresh something in the DOM, relink everything in its subtree
    onRefreshAnswerTab: function(SubtreeDOM) {
        // Submit answers ajax
        SubtreeDOM.find(s.postAnswerFormSelector).submit(function(event) {
            Utils.SubmitFormAjax(event, this,
                function(result) {
                    var $answer_tab = $(result.id_selector);
                    $answer_tab.html(result.html);

                    ForumPage.onRefreshAnswerTab($answer_tab);
                }, 
                function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus)
                }
            );
        });
        // Get the reply form ajax
        SubtreeDOM.find(s.getReplyLinkSelector).click( function(event) {
            event.preventDefault();
            var $link = $(this);
            var $reply_form = $link.parents('.answer-footer').find('.reply-form');
            if (!($reply_form.hasClass('active'))) {
                $.ajax({
                    type: "get",
                    url: this.href,
                    success: function(response) {
                        $reply_form.html(response.html).slideDown();
                        $reply_form.addClass('active');

                        ForumPage.onRefreshAnswerTab($reply_form);
                    }
                })
            }
        });
        // Get the bestanswers or discussion view ajax
        var $discussions = SubtreeDOM.find(s.discussionLinkSelector);
        var $best_answers = SubtreeDOM.find(s.bestanswersLinkSelector);
        ($best_answers.add($discussions)).click(function(event) {
            event.preventDefault();
            var $link = $(this);
            var $forum_answers = $link.parents('.forum-answers').parent();
            $.ajax({
                type: "get",
                url: this.href,
                success: function(response) {
                    $forum_answers.html(response.html).slideDown();

                    ForumPage.onRefreshAnswerTab($forum_answers);
                }
            })
        });
        // Upvote posts and answers
        var $upvote_posts = SubtreeDOM.find(s.upvotePostFormSelector);
        var $upvote_answers = SubtreeDOM.find(s.upvoteAnswerFormSelector);
        ($upvote_posts.add($upvote_answers)).click(function(event) {
            Utils.SubmitFormAjax(event, this,
                function(result) {
                    $(result.id_selector).html(result.html);

                    ForumPage.onRefreshAnswerTab($(result.id_selector));
                }, 
                function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus);
                }
            );
        });
    },
};

ForumPage.init();