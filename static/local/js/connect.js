jQuery( document ).ready(function( $ ) {
    ConnectGlobal.init();

});

var ConnectGlobal = (function() {
    var me = { 
        settings: {
            dismissableAlerts: $(".dismissable-alert"),
            emailConfirmationLinks: $(".email-confirmation-link"),
            campusnetPopover: $("#campusnet-popover"),
            forgotPasswordPopover: $("#forgot-pw-popover"),
            localeLinks: $('.locale-change-link'),
            helpsigns: $('.help-sign'),
            fileUploads: $('.file-input'),
            ckeditorNonEditableSelector: '.rich-cke-text',
            ckeditorEditableSelector: ".ckeditor"
        },
        global_variables: {
            boundForumActions: false, // Has ForumPage.bindUIActions been called?
        }
    }, s, globals;

    me.init = function() {
        s = this.settings;
        globals = this.global_variables;
        this.bindUIActions();
        //this.refreshCKInline();
        //this.refreshCK();

        if ($('.explore-page').length > 0) { ExplorePage.init(); }
        else if ($('.course-page').length > 0) { CoursePage.init(); }
        else if ($('.profile-page').length > 0) { ProfilePage.init(); ForumPage.init(); CoursePage.init(); Activities.init(); } // ForumPage needed to upvote forum posts
        else if ($('.forum-page').length > 0) { ForumPage.init(); } 
        else if ($('.welcome-page').length > 0) { WelcomePage.init(); } 
        else if ($('.dashboard-page').length > 0) { ForumPage.init(); CoursePage.init(); Activities.init(); } // ForumPage needed to upvote forum posts, add dashboard page when needed
        else if ($('.comments-page').length > 0) { CoursePage.init(); }
        else if ($('.homework-dashboard-page').length > 0) { HomeworkDashboard.init(); }


    };


    me.refreshCK = function(subtree) {
        if (typeof(subtree) === 'undefined') subtree = $('body');
        subtree.find(s.ckeditorEditableSelector).each(function(i, el) {
            var el_id = $(el).attr('id');
            var editor = undefined;
            
            if (el_id in CKEDITOR.instances) {
                delete CKEDITOR.instances[el_id];
            } 
            
            CKEDITOR.replace(el_id, {
                on: {
                    instanceReady: function(e) {
                        var node = e.editor.element.$;
                        if ($(node).attr("contenteditable") == "false") {
                            $(node).attr("contenteditable", true);
                            e.editor.setReadOnly(false);
                        }
                    }
                }
            });
            
        });
    };

    me.refreshCKInline = function(subtree) {
        if (typeof(subtree) === 'undefined') subtree = $('body');


        subtree.find(s.ckeditorNonEditableSelector).each(function(i, el) {
            var el_id = $(el).attr('id');
            var editor = undefined;
            if (el_id in CKEDITOR.instances) {
                delete CKEDITOR.instances[el_id];
            } 
           
            editor = CKEDITOR.inline(el_id, {
                on: {
                    instanceReady: function() {
                        this.editable(false);
                        MathJax.Hub.Queue(["Typeset",MathJax.Hub, el_id]); 
                        
                    }
                } 
            });  
        });

    };

    // setCookie, getCookie and checkCookie were taken from w3schools.com
    // http://www.w3schools.com/js/js_cookies.asp
    me.setCookie = function (cname, cvalue, days, hours, min, sec) {
        // Default to 1 day long lifetime
        var d = new Date();
        if (typeof(days) === "undefined") days = 1;
        if (typeof(hours) === "undefined") hours = 0;
        if (typeof(min) === "undefined") min = 0;
        if (typeof(sec) === "undefined") sec = 0;

        d.setTime(d.getTime() + (days*24*60*60*1000) + (hours*60*60*1000) + (min*60*1000) + (sec*1000));
        var expires = "expires="+d.toUTCString();
        document.cookie = cname + "=" + cvalue + "; " + expires;
    };

    me.getCookie = function(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i=0; i<ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1);
            if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
        }
        return "";
    };

    me.checkCookie = function(cname) {
        var cvalue = getCookie(cname);
        if (cvalue != "") {
            return true;
        } else {
            return false;
        }
    };

    me.getCookieAndDelete = function(cname) {
        var cookie = this.getCookie(cname);
        this.deleteCookie(cname);
        return cookie;
    };

    me.deleteCookie = function(cname) {
        document.cookie = cname + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/";
    };

    me.getUrlParameter = function(sParam) {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++) {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam) 
            {
                return sParameterName[1];
            }
        }
        return null;         
    }

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
        s.forgotPasswordPopover.tooltip({title: 'Forgot Password?'});
        // Locale change
        s.localeLinks.click(function(event) {
            $(this).find('form')[0].submit();
        });

        s.helpsigns.tooltip();
   
    };
    



    return me;
}());
