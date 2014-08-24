jQuery( document ).ready(function( $ ) {


    ConnectGlobal.init();

    if ($('.explore-page').length > 0) { ExplorePage.init(); }
    else if ($('.course-page').length > 0) { CoursePage.init(); ForumPage.init(); }
    else if ($('.forum-page').length > 0) { ForumPage.init(); }
    else if ($('.welcome-page').length > 0) { WelcomePage.init(); }

});

var ConnectGlobal = (function() {
    var me = { 
        settings: {
            dismissableAlerts: $(".dismissable-alert"),
            emailConfirmationLinks: $(".email-confirmation-link"),
            campusnetPopover: $("#campusnet-popover"),
            localeLinks: $('.locale-change-link'),
            activities: $('.recent_activities')
        },
        global_variables: {
            activities_pagenum: 1
        },
    }, s, globals;

    me.init = function() {
        s = this.settings;
        globals = this.global_variables;
        this.bindUIActions();
    };

    me.loadNewActivities = function() {
        var last_id = $(".new_activities_form > input[name='last_id']").val();
        if (last_id) {
            var action;
            if ($('.dashboard-page').length > 0) {
                action = 'load_new_dashboard_activities';
            }
            else if ($('.course-page').length > 0) {
                action = 'load_new_course_activities';
            }
            window.console.log(action);
            $.ajax({
                type: "GET",
                url: action,
                data: {"last_id": last_id},
                success: function(data) {
                    var json_data = $.parseJSON(data);
                    status = json_data.status;
                    html = json_data.html.trim();
                    new_last_id = json_data.new_last_id;
                    if (status == "OK" && new_last_id) {
                        $(".new_activities_form > input[name='last_id']").val(new_last_id);
                        $(html).hide().prependTo(s.activities).slideDown("slow");
                        //s.activities.prepend(html).slideDown("slow");

                    }
                },
                complete: function() {   
                    setTimeout(me.loadNewActivities, 10000);       
                }

            });
        }
    };

    me.bindUIActions = function() {
        // Activate Alerts
        s.dismissableAlerts.alert();
        // Email confirmation link
        s.emailConfirmationLinks.click( function() {
            $.get($(this).attr("src"));
        });

        // Tooltip for CampusNet
        s.campusnetPopover.tooltip({title: 'Please log in with your CampusNet credentials!'});

        // Locale change
        s.localeLinks.click(function(event) {
            $(this).find('form')[0].submit();
        });

        $(document).scroll(function () {
            
            if ($(window).scrollTop() == ($(document).height() - $(window).height())) {
                /* Load more activities */
                var action;
                if ($('.dashboard-page').length > 0) {
                    action = 'load_dashboard_activities';
                }
                else if ($('.course-page').length > 0) {
                    action = 'load_course_activities';
                }
                $.ajax({
                    type: "GET",
                    url: action,
                    data: {"page": globals.activities_pagenum + 1},
                    success: function(data) {
                        var json_data = $.parseJSON(data);
                        status = json_data.status;
                        html = json_data.html;
                        if (status == "OK") {
                            globals.activities_pagenum += 1;
                            s.activities.append(html);
                        }
                    },
                    error: function() {
                        //fail silently
                    }
                });
            }
        });

        setTimeout(this.loadNewActivities, 10000);


    };

    return me;
}());

// ****************************************************
// TODO: Break the code below into separate files
//
jQuery( document ).ready(function( $ ) {


    // Datetimepicker and Time handlers
    $('.homework-start-datetime').datetimepicker({
        defaultDate: moment().startOf("hour"),
        minDate: moment(),
        maxDate: moment().add("years", 1),
        pick12HourFormat: false
    });
    $('.homework-deadline-datetime').datetimepicker({
        defaultDate: moment().add("weeks", 1).endOf("day"),
        minDate: moment(),
        maxDate: moment().add("years", 1),
        pick12HourFormat: false
    });
    $('.homework-datetime-input').click(function() {
        var $parent = $(this.parentNode);
        var $button = $parent.find(".homework-datetime-button");
        $button.parent().data("DateTimePicker").show();
    });
    $('.homework-form').ready(function() {
        var tz = $(this).find('input[name="timezone"]');
        tz.val( moment().zone() )
    });

    // Forum register form
    $('.forumregistration-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                $(".forum-management").html(result.html)
            }, 
            function(jqXHR, textStatus, errorThrown) {
                $(".forum-management").html(textStatus)
            }
        );
    });

    // Get reply form for forum answer reply
    $('.forumregistration-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                $(".forum-management").html(result.html)
            }, 
            function(jqXHR, textStatus, errorThrown) {
                $(".forum-management").html(textStatus)
            }
        );
    });


    // Confirm the registration of a student for a course. 
    $(".confirm_registration").submit(function(event) {
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
    });

    $(".send-mass-email-form").submit(function(event) {
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
    });

    $('.selectAll').click(function(event) {   
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
    });


});