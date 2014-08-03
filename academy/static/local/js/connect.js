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
        }
    }, s;

    me.init = function() {
        s = this.settings;

        this.bindUIActions();
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