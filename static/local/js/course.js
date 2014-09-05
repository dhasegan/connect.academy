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
            displayFlaggedReviewSelector: '.display-flagged-review',

            // Teacher management
            confirmRegistrationForm: $(".confirm_registration"),
            sendEmailForm: $(".send-mass-email-form"),
            selectAll: $('.selectAll'),
            homeworkStartDatetime: $('.homework-start-datetime'),
            homeworkDeadlineDatetime: $('.homework-deadline-datetime'),
            homeworkDatetimeInput: $('.homework-datetime-input'),
            homeworkForm: $('.homework-form'),
            addExtraTag: $('.add-extratag'),
            extraTagForm: $('.extratag-form'),
        }
    }, s;

    me.init = function() {
        s = me.settings;

        $(s.ratingTooltipsSelector).tooltip()
        this.setupMyRatings();

        // Datetimepicker and Time handlers
        s.homeworkStartDatetime.datetimepicker({
            defaultDate: moment().startOf("hour"),
            minDate: moment(),
            maxDate: moment().add("years", 1),
            pick12HourFormat: false
        });
        s.homeworkDeadlineDatetime.datetimepicker({
            defaultDate: moment().add("weeks", 1).endOf("day"),
            minDate: moment(),
            maxDate: moment().add("years", 1),
            pick12HourFormat: false
        });


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
        $(s.displayFlaggedReviewSelector).click(this.displayFlaggedReviewClick);

        s.confirmRegistrationForm.submit(this.confirmRegistrationFormSubmit);
        s.sendEmailForm.submit(this.sendEmailFormSubmit);
        s.selectAll.click(this.selectAllClick);
        s.extraTagForm.submit(this.extraTagFormSubmit);

        s.homeworkDatetimeInput.click(function() {
            var $parent = $(this.parentNode);
            var $button = $parent.find(".homework-datetime-button");
            $button.parent().data("DateTimePicker").show();
        });
        s.homeworkForm.ready(function() {
            var tz = $(this).find('input[name="timezone"]');
            tz.val( moment().zone() );
        });
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

    me.displayFlaggedReviewClick = function(event) {
        event.preventDefault();
        $(this).toggleClass('hidden');
        $(this).parents(s.reviewBlockSelector).find('.review').toggleClass('hidden');
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
    };

    // Confirm the registration of a student for a course.
    me.confirmRegistrationFormSubmit = function(event) {
        var form = $(this);
        var data = form.serialize();
        var courseID = $("[name='courseID']", form).val();
        event.preventDefault();
        $.ajax({
            'url': form.attr('action'),
            'type': "POST",
            'data': data,
            'success': function(data) {
                if (data == "OK") {
                    $('#register_button' + courseID).text('Pending Registration...');
                    $('#register_button' + courseID).attr('disabled',true);
                    $("#registrationModal"+courseID).modal('hide');
                }
            }
        });
    };

    me.sendEmailFormSubmit = function(event) {
        var form = $(this);
        var data = form.serialize();
        var courseID = $("#course",form).val();
        var success_div_id = "email-success" + courseID;
        var error_div_id = "email-error" + courseID;
        event.preventDefault();
        var checkedAtLeastOne = false;
        $('input[type="checkbox"]',form).each(function() {
            if ($(this).is(":checked")) {
                checkedAtLeastOne = true;
            }
        });
        if (checkedAtLeastOne) {
            $.ajax({
                'url': form.attr('action'),
                'type': 'POST',
                'data': data,
                'success': function(data) {
                    if (data == "OK") {
                        $('.email-success',form).show();
                        $('.email-success',form).html('Your email was sent!');
                        $('.email-success',form).delay(2000).fadeOut(300);
                    }
                    else {
                        $('.email-error',form).show();
                        $('.email-error',form).html(data);
                        $('.email-error',form).delay(3000).fadeOut(300);
                    }
                }
            });
        }
        else {
            $('.email-error',form).show();
            $('.email-error',form).html("Please select at least one recepient.");
            $('.email-error',form).delay(2000).fadeOut(300);
        }
    };

    me.selectAllClick = function(event) {
        if(this.checked) {
        // Iterate each checkbox
            $(this).parent().parent().find("input[type='checkbox']").each(function() {
                this.checked = true;
            });
        }
        else {
            $(this).parent().parent().find("input[type='checkbox']").each(function() {
                this.checked = false;
            });
        }
    }

    return me;
}());
