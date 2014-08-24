var CoursePage = (function() {
    var me = { 
        settings: {
            // Ratings settings
            courseRatingsSelector: ".course-ratings",
            ratingTooltipsSelector: '.rating-tooltip',

            ratingFormSelector: ".rating-form",
            ratingClarifications: $('.ratings-tooltip-clarif'),
            expandRatingSubmit: $('.expand-rating-submit'),

            ratingStarsSelector: '.rating-stars',
            starOnURL: '/static/images/star-on.png',
            starOffURL: '/static/images/star-off.png',
            starHalfURL: '/static/images/star-half.png',

            // Reviews settings
            reviewsWrapperSelector: '.reviews-display',

            reviewFormSelector: '.submit-review-form',
            reviewBlockSelector: '.review-block',
            submitReviewButton: $('.submit-btn'),
            reviewCollapser: $('#submitreview'),
            expandReviewSubmit: $('.expand-review-submit'),

            // Vote review settings
            upvoteReviewFormSelector: '.upvote-review-form',
            flagReviewFormSelector: '.flag-review-form',

            // Upvote review
            upvoteButtonSelector: '.upvote-btn',

            // Flag review
            reviewFlagSelector: '.review-flag',
            flagButtonSelector: '.flag-btn',

            // Teacher management
            addExtraTag: $('.add-extratag'),
            extraTagForm: $('.extratag-form'),
        }
    }, s;

    me.init = function() {
        s = me.settings;

        $(s.ratingTooltipsSelector).tooltip()
        this.setupMyRatings();

        this.bindUIActions();
    };

    me.setupMyRatings = function() {
        $(s.ratingStarsSelector).raty({
            starOn: s.starOnURL,
            starOff: s.starOffURL,
            starHalf: s.starHalfURL,
            number: 5,
            mouseover: function(score, evt) {
                $(this).parents('form').find('.rating-my-score').text(score);
            },
            mouseout: function() {
                var form = $(this).parents('form');
                var score = form.find('input[name="old_score"]').val();
                form.find('.rating-my-score').text(score);
            },
            noRatedMsg: "To rate please log in!",
            score: function() {
                var form = $(this).parents('form');
                form.find('input[name="rating_value"]')
                return form.find('input[name="rating_value"]').val()
            },
            click: function(score, evt) {
                var form = $(this).parents('form');
                form.find('input[name="rating_value"]').val(score)
                var user = form.find('input[name="username"]')
                if (user.length > 0) {
                    form.submit();
                }
            },
            readOnly: function() {
                var is_auth = $(this).parents('form').find('input[name="authenticated"]')
                return (is_auth.length == 0);
            },
            hints: ['1', '2', '3', '4', '5']
        });

        s.ratingClarifications.tooltip({
            placement: 'top',
            title: function() {
                var type = $(this).parents('form').find('input[name="rating_type"]').val();
                if (type == 'ALL') {
                    return "How do you rate the course in general?"
                } else if (type == 'WKL') {
                    return "More stars means higher workload"
                } else if (type == 'DIF') {
                    return "More stars means higher difficulty"
                } else if (type == 'PRF') {
                    return "How do you rate this professor?"
                } 
            }
        });
    }

    me.bindUIActions = function() {
        $(s.ratingFormSelector).submit(this.ratingFormSubmit);
        $(s.reviewFormSelector).submit(this.reviewFormSubmit);
        $(s.upvoteReviewFormSelector).submit(this.upvoteReviewFormSubmit);
        $(s.flagReviewFormSelector).submit(this.flagReviewFormSubmit);
        s.extraTagForm.submit(this.extraTagFormSubmit);
    };

    me.ratingFormSubmit = function(event) {
        Utils.SubmitFormAjax(event, this, 
            function(response) {
                $(s.courseRatingsSelector).replaceWith(response.ratings);
                $(s.ratingTooltipsSelector).tooltip()
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    me.reviewFormSubmit = function(event) {
        s.submitReviewButton.attr('disabled', 'disabled');
        s.reviewCollapser.collapse('hide');
        s.expandReviewSubmit.addClass('hidden');

        Utils.SubmitFormAjax(event, this, 
            function(response) {
                $(s.reviewsWrapperSelector).prepend("<hr>" + response.html);
                item = $(s.reviewsWrapperSelector).find(s.reviewBlockSelector).first();

                item.find(s.upvoteReviewFormSelector).submit(me.upvoteReviewFormSubmit);
                item.find(s.flagReviewFormSelector).submit(me.flagReviewFormSubmit);
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    me.upvoteReviewFormSubmit = function(event) {
        $(this).find(s.upvoteButtonSelector).attr('disabled', 'disabled');
        var upvoteForm = $(this);
        var parent = upvoteForm.parent();

        Utils.SubmitFormAjax(event, this, 
            function(response) {
                upvoteForm.replaceWith(response.html);
                parent.find(s.upvoteReviewFormSelector).submit(me.upvoteReviewFormSubmit);
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    }

    me.flagReviewFormSubmit = function(event) {
        $(this).find(s.flagButtonSelector).attr('disabled', 'disabled');
        var $reviewFlag = $(this).parents(s.reviewFlagSelector);
        $reviewFlag.addClass("hidden");

        Utils.SubmitFormAjax(event, this, 
            function(response) {
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    me.extraTagFormSubmit = function(event) {
        var alphanumeric = /^([a-zA-Z0-9]+)$/;
        var tagName = $(this).find('.extratag-input').val();
        if (alphanumeric.test(tagName) == false) {
            s.extraTagForm.popover('show');
            event.preventDefault();
            return ;
        }

        Utils.SubmitFormAjax(event, this, 
            function(response) {
                s.extraTagForm.parent().html(tagName);
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    }

    return me;
}());
