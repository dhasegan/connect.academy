var CoursePage = (function() {
    var me = { 
        settings: {
            // Ratings settings
            myRatingsSelector: ".my-ratings",
            aggRatingsSelector: ".agg-ratings",

            ratingFormSelector: ".rating-form",
            ratingClarifications: $('.ratings-tooltip-clarif'),
            ratingTooltips: $('.ratings-tooltip'),

            ratingStarsSelector: '.rating-stars',
            starOnURL: '/static/images/star-on.png',
            starOffURL: '/static/images/star-off.png',
            starHalfURL: '/static/images/star-half.png',

            // Reviews settings
            reviewsPanelSelector: '.reviews-panel',
            reviewFormSelector: '.submit-review-form',
            reviewBlockSelector: '.review-block',

            // Vote review settings
            reviewRateFormSelector: '.review-rate-form',
            reviewRatingSelector: '.review-rate',
            reviewRatingBadgeSelector: '.review-score-badge'
        }
    }, s;

    me.init = function() {
        s = me.settings;

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

        s.ratingTooltips.tooltip({
            placement: 'left',
            html: false,
            title: 'Log in to vote!'
        });
        s.ratingTooltips.attr('data-original-title', 'Log in to vote!')

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
        $(s.reviewRateFormSelector).submit(this.reviewVoteFormSubmit);
    };

    me.ratingFormSubmit = function(event) {
        Utils.SubmitFormAjax(event, this, 
            function(response) {
                $(s.aggRatingsSelector).replaceWith(response.agg_ratings);
                $(s.myRatingsSelector).replaceWith(response.my_ratings);
                me.setupMyRatings();
                $(s.ratingFormSelector).submit(me.ratingFormSubmit);
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    me.reviewFormSubmit = function(event) {
        Utils.SubmitFormAjax(event, this, 
            function(response) {
                $(s.reviewsPanelSelector).replaceWith(response.html);
                $(s.reviewFormSelector).submit(me.reviewFormSubmit);
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    me.reviewVoteFormSubmit = function(event) {
        var $reviewRating = $(this).parents(s.reviewRatingSelector);
        var $reviewBlock = $(this).parents(s.reviewBlockSelector);
        Utils.SubmitFormAjax(event, this, 
            function(response) {
                $reviewBlock.find(s.reviewRatingBadgeSelector).text(response.score);
                $reviewRating.addClass("hidden");
            }, function(jqXHR, textStatus, errorThrown) {
            }
        );
    };

    return me;
}());
