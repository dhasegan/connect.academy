var ForumPage = (function() {
    var me = {
        settings: {
            // Filters
            postFilters: $('.post-filter'),
            currentPostFilter: $('.current-post-filter'),
            postFilterNameSelector: '.post-filter-name',

            // Posts sidebar
            posts: $('.forum-post'),

            // Answers tabs
            flagPostLinkSelector: '.flag-post-link',
            flagAnswerLinkSelector: '.flag-answer-link',
            displayFlaggedPostSelector: '.display-flagged-post',
            displayFlaggedAnswerSelector: '.display-flagged-answer',
            postAnswerFormSelector: '.forumpostnewanswer-form',
            postAnswerButtonSelector: '.newanswer-btn',
            getReplyLinkSelector: '.getreplyform-link',
            discussionLinkSelector: '.discussion-link',
            bestanswersLinkSelector: '.bestanswers-link',
            upvotePostFormSelector: '.upvote-post-form',
            upvoteAnswerFormSelector: '.upvote-answer-form',

            ckeditorNonEditable: $('.rich-cke-text'),

            // New post page
            newPostForm: $('.forumnewpost-form'),
            newPostButton: $('.newpost-btn'),

            //Follow-unfollow post
            postFollowForm: $('form.post-follow-form'),
            postFollowContainerSelector: 'div.post-follow-container'
        }
    }, s;

    me.init = function() {
        s = me.settings;

        // Index the posts based on the filters
        me.indexPosts();

        // Bind ui actions for answers tab
        me.onRefreshAnswerTab($('html'));
        me.bindUIActions();
        //ConnectGlobal.refreshCKInline();

    };

    me.bindUIActions = function() {

        // On Filter change
        s.postFilters.click( function() {
            s.postFilters.removeClass("hidden");
            $(this).addClass("hidden");
            s.currentPostFilter.find(s.postFilterNameSelector).text(this.text);

            ForumPage.indexPosts();
        });

        // On new post submit
        s.newPostForm.submit( function(event) {
            s.newPostButton.attr('disabled', 'disabled');
        });

        var upvote_selector = s.upvotePostFormSelector + ", " + s.upvoteAnswerFormSelector;

        $(document).on("click", upvote_selector, function(event) {
            Utils.SubmitFormAjax(event, this,
                function(result) {
                    for (idx in result.id_selectors) {
                        $(result.id_selectors[idx]).html(result.html);
                    }
                }, 
                function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus);
                }
            );
        });
        

    };

    me.indexPosts = function() {
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
    };



    // Refresh something in the DOM, relink everything in its subtree
    me.onRefreshAnswerTab = function(SubtreeDOM) {
        if (typeof(SubtreeDOM) === "undefined" ) SubtreeDOM = $('html');
        // Submit answers ajax
        SubtreeDOM.find(s.postAnswerFormSelector).submit(function(event) {
            $(this).find(s.postAnswerButtonSelector).attr('disabled', 'disabled');
            // Add CKEDITOR data into the textarea
            var content = $($(this).find("iframe")[0]).contents().find("body")[0].innerHTML;
            $(this).find("textarea[name='text']").val(content);
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
                        var textarea_id = $(response.html).find("textarea[name='text']").attr("id");
                        //CKEDITOR.replace(textarea_id);
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
        // Flag posts and answers
        SubtreeDOM.find(s.flagPostLinkSelector).click( function(event) {
            $(this).toggleClass('hidden');
            var form = $(this).parents('form')[0];
            Utils.SubmitFormAjax(event, form,
                function(result) {
                }, 
                function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus)
                }
            );
        });
        SubtreeDOM.find(s.flagAnswerLinkSelector).click( function(event) {
            $(this).toggleClass('hidden');
            var form = $(this).parents('form')[0];
            Utils.SubmitFormAjax(event, form,
                function(result) {
                }, 
                function(jqXHR, textStatus, errorThrown) {
                    console.log(textStatus)
                }
            );
        });
        // Display blocked content
        SubtreeDOM.find(s.displayFlaggedPostSelector).click( function(event) {
            event.preventDefault();
            $(this).toggleClass('hidden');
            $(this).parents('.post-details').find('.post-text').toggleClass('hidden');
        });
        SubtreeDOM.find(s.displayFlaggedAnswerSelector).click( function(event) {
            event.preventDefault();
            $(this).toggleClass('hidden');
            $($(this).parent()).find('.answer-body').toggleClass('hidden');
        });
        // Upvote posts and answers
        
        // Follow post
        SubtreeDOM.find(s.postFollowContainerSelector).on("submit", "form", function(event) {
            event.preventDefault();
            form = $(this);
            container = form.parent().parent();
            $.ajax({
                type: form.attr("method"),
                url: form.attr("action"),
                data: form.serialize(),
                success: function(data) {
                    if (data['status'] == "OK") {;
                        container.empty().hide().append(data['html']).fadeIn("slow");
                    }
                }


            });
        });
       ConnectGlobal.refreshCKInline(SubtreeDOM);
       ConnectGlobal.refreshCK(SubtreeDOM); 
    };

    return me;
}());
