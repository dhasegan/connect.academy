var CoursePage = (function() {
    var me = {
        settings: {
            coursePage: ".course-page",
            // Ratings settings
            courseRatingsSelector: ".course-ratings",
            ratingTooltipsSelector: '.rating-tooltip',

            ratingFormSelector: ".rating-form",
            ratingClarifications: '.ratings-tooltip-clarif',
            expandRatingSubmit: '.expand-rating-submit',

            ratingStarsSelector: '.rating-stars',
            starOnURL: '/static/images/star-on.png',
            starOffURL: '/static/images/star-off.png',
            starHalfURL: '/static/images/star-half.png',
            changeRegistrationModuleURL: 'change_reg_module',

            // Reviews settings
            reviewsWrapperSelector: '.reviews-display',

            reviewFormSelector: '.submit-review-form',
            reviewBlockSelector: '.review-block',
            submitReviewButton: '.submit-btn',
            reviewCollapser: '#submitreview',
            expandReviewSubmit: '.expand-review-submit',

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
            confirmRegistrationForm: ".confirm_registration",
            sendEmailForm: ".send-mass-email-form",
            selectAll: '.selectAll',
            homeworkStartDatetime: '.homework-start-datetime',
            homeworkDeadlineDatetime: '.homework-deadline-datetime',
            homeworkDatetimeInput: '.homework-datetime-input',
            homeworkForm: '.homework-form',
            addExtraTag: '.add-extratag',
            extraTagForm: '.extratag-form',
            taContainerSelector: '.teaching-assistants > ul.no-bullet',
            taPermissionsFormSelector: '.TA-permissions-form',
            newTAFormSelector: '#new-ta-form',
            removeTAFormSelector: ".remove-ta-form",
            TAPermissionsIdPrefix: '#ta-permissions-li',
            pendingRegistrationsTable: "#course-pending-registrations",
            registeredStudentsTable: "#course-registered-students",
            registrationModuleSelector: "select.choose-module",
            loadCourseTabUrl: "load_course_tab",
            coursePageTabSelector: ".course_page_tab",
            sidebar2Container: "#course_sidebar_tabs",
            mainContent: "#course_main_content",
            loadingCourseTab: ".loading-course-tab",
            courseStudentsDataTableConfig: {
                "columnDefs": [
                    {
                        "orderable": false,
                        "targets": [0]
                    }
                ],
                "columns": [
                        null,
                        null,
                        null,
                        { "orderDataType": "dom-select" }
                    ],
                "order": [[1,'asc']]
            },
            
        },
        global_variables: {
            availableCoursePages: {
                "activity": {
                    "loaded": false,
                },
                "info": {
                    "loaded": false,
                },
                "connect": {
                    "loaded": false,
                },
                "wiki": {
                    "loaded": false,
                },
                "resources": {
                    "loaded": false,
                },
                "teacher": {
                    "loaded": false,
                },
            },
            busy: false
        }

    }, s, globals;

    me.init = function() {
        s = me.settings;
        globals = me.global_variables;

        var page = ConnectGlobal.getUrlParameter("page");
        var teacher_page = ConnectGlobal.getUrlParameter("teacher_page");
        if (!page) {
            if (teacher_page) {
                page = "teacher";
            }
            else {
                page = "activity";
            }
        }
        if (page in globals.availableCoursePages) {
            globals.availableCoursePages[page].loaded = true; 
        }


        this.bindUIActions();
        this.bindUIActionsForTab(page);
        
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

        $(s.ratingClarifications).tooltip({
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
    };

    me.bindUIActions = function() {

        $(s.coursePage).on("submit", s.ratingFormSelector, this.ratingFormSubmit);
        $(s.coursePage).on("submit", s.reviewFormSelector, this.reviewFormSubmit);
        $(s.coursePage).on("submit", s.upvoteReviewFormSelector, this.upvoteReviewFormSubmit);
        $(s.coursePage).on("submit", s.flagReviewFormSelector, this.flagReviewFormSubmit);
        $(s.coursePage).on("submit", s.displayFlaggedReviewSelector, this.displayFlaggedReviewClick);

        $(s.coursePage).on("submit", s.confirmRegistrationForm, this.confirmRegistrationFormSubmit);
        $(s.coursePage).on("submit", s.sendEmailForm, this.sendEmailFormSubmit);
        $(s.coursePage).on("click", s.selectAll, this.selectAllClick);
        $(s.coursePage).on("submit", s.extraTagForm, this.extraTagFormSubmit);

        $(s.coursePage).on("click", s.homeworkDatetimeInput, function() {
            var $parent = $(this.parentNode);
            var $button = $parent.find(".homework-datetime-button");
            $button.parent().data("DateTimePicker").show();
        });
        $(s.coursePage).on("ready", s.homeworkForm, function() {
            var tz = $(this).find('input[name="timezone"]');
            tz.val( moment().zone() );
        });


        


        $(s.coursePage).on("click", s.coursePageTabSelector, function() {
            
            page = $(this).data('page');
            if (!globals.availableCoursePages[page].loaded) { 
                me.loadCoursePage(page);
            }
        });

        $(s.coursePage).on("change", s.registrationModuleSelector, function() {
            var success = $($(this).closest('td')[0]).find('.validation-ok')[0];
            var warning = $($(this).closest('td')[0]).find('.validation-warning')[0];
            var error =   $($(this).closest('td')[0]).find('.validation-error')[0];
            

            var name = $(this).attr('name');
            var val = $(this).val();
            data = {
                'csrfmiddlewaretoken': ConnectGlobal.getCookie('csrftoken')
            }
            data[name] = val;

            $.ajax({
                'url': s.changeRegistrationModuleURL,
                'type': "POST",
                'data': data,
                'success': function(data) {
                    json_data = $.parseJSON(data);
                    var container = null;
                    if (json_data.status == "OK") {
                        container = success;
                    }
                    else if (json_data.status == "Warning") {
                        container = warning;
                    }
                    else if (json_data.status == "Error") {
                        container = error;
                    }
                    $(container).html(json_data.message).show();
                    setTimeout(function() {
                        $(container).hide();
                    }, 2000);
                    
                },
                'error': function() {
                    container = error;
                    $(container).html("Error processing request.").show()
                    setTimeout(function() {
                        $(container).find(".validation-error").hide();
                    }, 2000);
                }
            });
        });


        // AJAX to remove TA
        $(s.coursePage).on('submit', s.removeTAFormSelector, function(event) {
            event.preventDefault();
            form = $(this);
            $.ajax({
                'url': form.attr('action'),
                'type': form.attr('method'),
                'data': form.serialize(),
                'success': function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        form.closest(".modal").modal('toggle');
                        setTimeout(function() {
                            $(s.TAPermissionsIdPrefix + json_data.ta_id).remove();
                        }, 500);
                        
                    }
                    else if (json_data.status == "Warning") {
                        form.find(".warning").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".warning").hide();
                        }, 3000);
                    }
                    else if (json_data.status == "Error") {
                        form.find(".error").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".error").hide();
                        }, 3000);
                    }
                },
                'error': function() {
                    form.find(".error").html("Error processing request.").show();
                    setTimeout(function() {
                        form.find(".error").hide();
                    }, 3000);
                }
            });
        });
        
        // Ajax to add new TA
        $(s.coursePage).on("submit", s.newTAFormSelector, function(event) {
            event.preventDefault();
            form = $(this);
            $.ajax({
                'url': form.attr('action'),
                'type': form.attr('method'),
                'data': form.serialize(),
                'success': function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        $(s.taContainerSelector).append(json_data.html);
                        form.find("input[type='email']").val('');
                    }
                    else if (json_data.status == "Warning") {
                        form.find(".warning").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".warning").hide();
                        }, 3000);
                    }
                    else if (json_data.status == "Error") {
                        form.find(".error").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".error").hide();
                        }, 3000);
                    }
                },
                'error': function() {
                    form.find(".error").html("Error processing request.").show();
                    setTimeout(function() {
                        form.find(".error").hide();
                    }, 3000);
                }
            });

        });
        

        // Ajax to change TA permissions
        $(s.coursePage).on('submit', s.taPermissionsFormSelector, function(event) {
            event.preventDefault();
            form = $(this);
            $.ajax({
                'url': form.attr('action'),
                'type': form.attr('method'),
                'data': form.serialize(),
                'success': function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        form.find(".success").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".success").hide();
                        }, 3000);
                    }
                    else if (json_data.status == "Warning") {

                        form.find(".warning").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".warning").hide();
                        }, 3000);
                    }
                    else if (json_data.status == "Error") {
                        form.find(".error").html(json_data.message).show();
                        setTimeout(function() {
                            form.find(".error").hide();
                        }, 3000);
                    }
                },
                'error': function() {
                    form.find(".error").html("Error processing request.").show();
                    setTimeout(function() {
                        form.find(".error").hide();
                    }, 3000);
                }
            });
        });
        
    };


    me.loadCoursePage = function(page) {
        if (!globals.busy) {
            globals.busy = true;
            var currentActiveMain = $(s.mainContent).find(".active");
            var currentActiveSide = $(s.sidebar2Container).find(".active");
            currentActiveMain.removeClass("active");
            currentActiveMain.removeClass("in");
            currentActiveSide.removeClass("active");
            currentActiveSide.removeClass("in");
            $(s.loadingCourseTab).show();
            $.ajax({
                'url': s.loadCourseTabUrl,
                'type': "GET",
                'data': {"page": page},
                'success': function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        sidebar_html = json_data.sidebar;
                        main_html = json_data.main;

                        $(s.sidebar2Container).append(sidebar_html);
                        $(s.mainContent).append(main_html);

                        if (!globals.availableCoursePages[page].loaded) {
                            me.bindUIActionsForTab(page);
                            ConnectGlobal.refreshCKInline($(main_html));
                        }
                        globals.availableCoursePages[page].loaded = true;
                        

                    }   
                },
                'error': function() {
                    container = error;
                    $(container).html("Error processing request.").show()
                    setTimeout(function() {
                        $(container).find(".validation-error").hide();
                    }, 2000);

                },
                'complete': function() {
                    $(s.loadingCourseTab).hide();
                    globals.busy = false;
                }
            });
        }
    };

    me.bindUIActionsForTab = function(page) {
        switch (page) {
            case "activity":
                console.log("binding for activity");
                Activities.init();
                if (!globals.availableCoursePages["connect"].loaded) {
                    ForumPage.init();
                }
                break;
            case "info":
                $(s.ratingTooltipsSelector).tooltip()
                this.setupMyRatings();
            case "connect":
                ForumPage.init();
                break;
            case "teacher":
                this.initDataTables();
                $(s.pendingRegistrationsTable).dataTable(s.courseStudentsDataTableConfig );
                $(s.registeredStudentsTable).dataTable(s.courseStudentsDataTableConfig );
                // Datetimepicker and Time handlers
                $(s.homeworkStartDatetime).datetimepicker({
                    defaultDate: moment().startOf("hour"),
                    minDate: moment(),
                    maxDate: moment().add("years", 1),
                    pick12HourFormat: false
                });

                $(s.homeworkDeadlineDatetime).datetimepicker({
                    defaultDate: moment().add("weeks", 1).endOf("day"),
                    minDate: moment(),
                    maxDate: moment().add("years", 1),
                    pick12HourFormat: false
                });
                break;
            default:
                break;
        }
    }

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
        $(s.submitReviewButton).attr('disabled', 'disabled');
        $(s.reviewCollapser).collapse('hide');
        $(s.expandReviewSubmit).addClass('hidden');

        Utils.SubmitFormAjax(event, this,
            function(response) {
                $(s.reviewsWrapperSelector).prepend("<hr>" + response.html);
                item = $(s.reviewsWrapperSelector).find(s.reviewBlockSelector).first();

                //item.find(s.upvoteReviewFormSelector).submit(me.upvoteReviewFormSubmit);
                //item.find(s.flagReviewFormSelector).submit(me.flagReviewFormSubmit);
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
                //parent.find(s.upvoteReviewFormSelector).submit(me.upvoteReviewFormSubmit);
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
            $(s.extraTagForm).popover('show');
            event.preventDefault();
            return ;
        }

        Utils.SubmitFormAjax(event, this,
            function(response) {
                $(s.extraTagForm).parent().html(tagName);
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
                    $('#register_button' + courseID).html('<b>Pending Registration</b>');
                    $('#register_button' + courseID).attr('disabled',true);
                    $('#register_button' + courseID).removeClass("btn-defaut").addClass("btn-success");
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
            $(this).closest('table').find("input[type='checkbox']").each(function() {
                this.checked = true;
            });
        }
        else {
            $(this).closest('table').find("input[type='checkbox']").each(function() {
                this.checked = false;
            });
        }
    };

    me.initDataTables = function() {
        if ($($(s.pendingRegistrationsTable).find("th td")).length < 4)
            s.courseStudentsDataTableConfig["columns"].pop(); // If Course_module is missing, remove it from config

        $.fn.dataTable.ext.order['dom-text'] = function  ( settings, col )
        {
            return this.api().column( col, {order:'index'} ).nodes().map( function ( td, i ) {
                return $('input', td).val();
            } );
        }
         
        /* Create an array with the values of all the input boxes in a column, parsed as numbers */
        $.fn.dataTable.ext.order['dom-text-numeric'] = function  ( settings, col )
        {
            return this.api().column( col, {order:'index'} ).nodes().map( function ( td, i ) {
                return $('input', td).val() * 1;
            } );
        }
         
        /* Create an array with the values of all the select options in a column */
        $.fn.dataTable.ext.order['dom-select'] = function  ( settings, col )
        {
            return this.api().column( col, {order:'index'} ).nodes().map( function ( td, i ) {
                return $('select', td).val() * 1;
            } );
        }
         
        /* Create an array with the values of all the checkboxes in a column */
        $.fn.dataTable.ext.order['dom-checkbox'] = function  ( settings, col )
        {
            return this.api().column( col, {order:'index'} ).nodes().map( function ( td, i ) {
                return $('input', td).prop('checked') ? '1' : '0';
            } );
        }
    }


    return me;
}());
