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
    }, s;

    me.init = function() {
        s = this.settings;
        
        this.bindUIActions();
        this.refreshCKInline();
        this.refreshCK();

        if ($('.explore-page').length > 0) { ExplorePage.init(); }
        else if ($('.course-page').length > 0) { CoursePage.init(); ForumPage.init(); Activities.init(); }
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
