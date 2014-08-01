var CoursePage = (function() {
    var me = { 
        settings: {
            ratingClarifications: $('.ratings-tooltip-clarif'),
            ratingTooltips: $('.ratings-tooltip'),

            ratingStars: $('.rating-stars'),

            starOnURL: '/static/images/star-on.png',
            starOffURL: '/static/images/star-off.png',
            starHalfURL: '/static/images/star-half.png',
        }
    }, s;

    me.init = function() {
        s = me.settings;

        s.ratingStars.raty( {
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

        bindUIActions();
    };

    function bindUIActions() {
    };


    return me;
}());
