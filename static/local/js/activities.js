var Activities = (function() {
    var me = {
        settings: {
        	activities: $(".recent_activities")
        },
        global_variables: {
        	activities_pagenum: 1
        }
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
                    //ForumPage.onRefreshAnswerTab();
                },
                complete: function() {   
                    setTimeout(me.loadNewActivities, 10000);       
                }

            });
        }
    };

    me.bindUIActions = function() {

    	/* Load more activities when reaching the bottom of the page */
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
                            if (html != "") {
                                globals.activities_pagenum += 1;
                                s.activities.append(html);
                            }
                        }
                    },
                    error: function() {
                        //fail silently
                    }
                });
            }
        });

        // Every 10 seconds, check for new activities
        setTimeout(this.loadNewActivities, 10000);
    };

    return me;
}());

