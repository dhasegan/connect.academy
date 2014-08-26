var ProfilePage = (function() {
    var me = { 
        settings: {
            editSummaryFormSelector: "#edit-summary-form",
            editSummaryButtonSelector: "#edit-summary-button",
            summaryContainerSelector: "#summary-container",
            summaryContentSelector: "#summary-content",

            profilePictureFormSelector: "#profile-picture-form",
            profilePictureSelector: "#profile-picture"
        }
    }, s;

    me.init = function() {
        s = this.settings;
        this.bindUIActions();
    };


    me.bindUIActions = function() {

        this.bindEditSummaryFormAction();
        this.bindEditSummaryButtonAction();
        $(s.profilePictureFormSelector).submit(function(event){ 
            event.preventDefault();
            $.ajax({
                type: "POST",
                url: "/new_profile_picture",
                data: new FormData( this ),
                processData: false,
                contentType: false,
                success:  function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        url = json_data.image_url + "?timestamp=" + new Date().getTime();
                        $(s.profilePictureSelector).attr("src", url).fadeIn();
                    }
                },
                error: function(jqXHR, textStatus, errorThrown){
                }
            });
        }) 
    };

    me.bindEditSummaryFormAction = function() {
        var summaryForm = $(s.editSummaryFormSelector);
        
        $(s.editSummaryFormSelector).submit(function(event) {
            event.preventDefault();
            $.ajax({
                type: "POST",
                url: "/edit_profile_summary",
                data: summaryForm.serialize(),
                success:  function(data) {
                    json_data = $.parseJSON(data);
                    if (json_data.status == "OK") {
                        html = json_data.html.trim();
                        $(s.summaryContainerSelector).html(html);
                        me.bindEditSummaryButtonAction();
                    }
                },
                error: function(jqXHR, textStatus, errorThrown){
                }
            });
        });
    };

    
    me.bindEditSummaryButtonAction = function() {
        $(s.editSummaryButtonSelector).click(function(event) {
            event.preventDefault();
            var csrf = $.cookie('csrftoken');
            var summary = $(s.summaryContentSelector).text();
            $(s.summaryContainerSelector).empty();
            s['summary_form_html'] = "<form id='edit-summary-form' method='POST' action='/edit_profile_summary'>";
            s['summary_form_html'] +=        "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'/>";
            s['summary_form_html'] +=            "<div class='form-group'>";
            s['summary_form_html'] +=                "<textarea rows='5' maxlength='300' name='summary' class='summary-textarea' placeholder='Write a short summary about yourself...'>";
            s['summary_form_html'] +=                    summary; 
            s['summary_form_html'] +=                "</textarea>";
            s['summary_form_html'] +=            "</div>";
            s['summary_form_html'] +=        "<input type='submit' class='btn btn-default' value='Save' />";
            s['summary_form_html'] += "</form>";
            $(s.summaryContainerSelector).append(s.summary_form_html);
            me.bindEditSummaryFormAction();
        });
    };

    me.nl2br = function (str, is_xhtml) {   
        var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';    
        return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
    }
    return me;
}());