var Activities = (function() {
    var me = {
        settings: {
        	activities: $(".activity-timeline"),
            isProfilePage: $('.profile-page').length > 0,
            isCoursePage: $('.course-page').length > 0,
            isDashboardPage: $('.dashboard-page').length > 0,
            oldest_activity_id_cookie: "oldest_activity_id",
            course_activity_tab: $("#course-activity-tab"),
            course_info_tab: $("#course-info-tab"),
            course_wiki_tab: $("#course-wiki-tab"),
            course_forum_tab: $("#course-forum-tab"),
            course_resources_tab: $("#course-resources-tab"),
            loading_activities_img: $("#loading-activities-gif"),
            
        },
        global_variables: {
            no_more: false, // No more (older) activities to load?
        	oldest_activity_id: null,
            busy: false
        }
    }, s, globals;

    me.init = function() {
    	s = this.settings;
        this.global_variables.oldest_activity_id = ConnectGlobal.getCookieAndDelete(s.oldest_activity_id_cookie);
    	globals = this.global_variables;
  
    	this.bindUIActions();
    };

    // Takes the sidebar tab as an argument and checks if it is active
    me.isTabActive = function(tab) {
        return tab.hasClass("active");
    };

    me.loadNewActivities = function() {
        var last_id = $(".new_activities_form > input[name='last_id']").val();
        if (last_id) {
            var action;
            if (s.isDashboardPage) {
                action = 'load_new_dashboard_activities';
            }
            else if (s.isCoursePage) {
                action = 'load_new_course_activities';
            }
            else if (s.isProfilePage) {
                action = 'load_new_profile_activities';
            }

            // In the course page, only load new activities when the user is on the activity tab
            // In other pages, always load new activities
            if (me.isTabActive(s.course_activity_tab) || !s.isCoursePage) {
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
                        //ForumPage.onRefreshAnswerTab();
                    },
                    complete: function() {   
                        setTimeout(me.loadNewActivities, 10000);       
                    }

                });
            }
            else {
                setTimeout(me.loadNewActivities, 10000);
            }
        }
    };

    me.bindUIActions = function() {

    	/* Load more activities when reaching the bottom of the page */
    	$(document).scroll(function () {
            if ($(window).scrollTop() == ($(document).height() - $(window).height())) {
                /* Load more activities */
                var action;
                if (s.isDashboardPage) {
                    action = 'load_dashboard_activities';
                }
                else if (s.isCoursePage) {
                    action = 'load_course_activities';
                }
                else if (s.isProfilePage) {
                    action = 'load_profile_activities';
                }
                // In the course page, only load more activities when the user is on the activity tab
                // In other pages, always load more activities as long as the server doesn't return empty html
                if ((me.isTabActive(s.course_activity_tab) || !s.isCoursePage) && !globals.no_more && !globals.busy) {
                    globals.busy = true;
                    s.loading_activities_img.show();
                    $.ajax({
                        type: "GET",
                        url: action,
                        data: globals.oldest_activity_id ? {"last_id": parseInt(globals.oldest_activity_id)} : {},
                        success: function(data,status,xhr) {
                            var json_data = $.parseJSON(data);
                            status = json_data.status;
                            html = json_data.html;
                            if (status == "OK") {
                                if (html != "") {
                                    oldest_activity = ConnectGlobal.getCookieAndDelete(s.oldest_activity_id_cookie);
                                    if (oldest_activity) {
                                        globals.oldest_activity_id = oldest_activity;
                                    }
                                    s.activities.append(html);
                                }
                                else  {
                                    globals.no_more = true;
                                }
                            }
                        },
                        error: function() {
                            //fail silently
                        },
                        complete: function() {
                            s.loading_activities_img.hide();
                            globals.busy=false;
                        }
                    });
                }
            }
        });

        // Every 10 seconds, check for new activities
        setTimeout(this.loadNewActivities, 10000);
    };

    return me;
}());

