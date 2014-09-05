jQuery( document ).ready(function( $ ) {

    ConnectGlobal.init();

});

var ConnectGlobal = (function() {
    var me = { 
        settings: {
            dismissableAlerts: $(".dismissable-alert"),
            emailConfirmationLinks: $(".email-confirmation-link"),
            campusnetPopover: $("#campusnet-popover"),
            localeLinks: $('.locale-change-link'),
            activities: $('.recent_activities'),
            helpsigns: $('.help-sign'),
            fileUploads: $('.file-input')
        },
        global_variables: {
            activities_pagenum: 1 // max page number of already loaded activities
        },
    }, s, globals;

    me.init = function() {
        s = this.settings;
        globals = this.global_variables;
        this.bindUIActions();

            if ($('.explore-page').length > 0) { ExplorePage.init(); }
            else if ($('.course-page').length > 0) { CoursePage.init(); ForumPage.init(); }
            else if ($('.profile-page').length > 0) { ProfilePage.init(); ForumPage.init(); CoursePage.init(); } // ForumPage needed to upvote forum posts
            else if ($('.forum-page').length > 0) { ForumPage.init(); } 
            else if ($('.welcome-page').length > 0) { WelcomePage.init(); } 
            else if ($('.dashboard-page').length > 0) { ForumPage.init(); CoursePage.init(); } // ForumPage needed to upvote forum posts, add dashboard page when needed
            else if ($('.comments-page').length > 0) { CoursePage.init(); }
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
            else if ($('.profile-page').length > 0) {
                action = 'load_new_profile_activities';
            }
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
                    //bind UI actions again to catch the newly loaded activities

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

        // General File uploads
        $(s.fileUploads).change(function () {
            var file_path = this.value.replace("C:\\fakepath\\", "");
            $(this).parents('.upload-file-wrapper').find('.upload-file-input').val(file_path);
        });

        // Tooltip for CampusNet
        s.campusnetPopover.tooltip({title: 'Please log in with your CampusNet credentials!'});

        // Locale change
        s.localeLinks.click(function(event) {
            $(this).find('form')[0].submit();
        });

        s.helpsigns.tooltip();

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
                else if ($('.profile-page').length > 0) {
                    action = 'load_profile_activities';
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
    
        // Every 10 seconds, check if there are any new activities
        setTimeout(this.loadNewActivities, 10000);


    };

    return me;
}());
