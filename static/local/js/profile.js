var ProfilePage = (function() {
    var me = { 
        settings: {
            editSummaryFormSelector: "#edit-summary-form",
            editSummaryButtonSelector: "#edit-summary-button",
            summaryContainerSelector: "#summary-container",
            summaryContentSelector: "#summary-content",
        }
    }, s;

    me.init = function() {
        s = this.settings;
        this.bindUIActions();
    };


    me.bindUIActions = function() {

        this.bindEditSummaryFormAction();
        this.bindEditSummaryButtonAction();
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
                        html = json_data.html;
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
            var summary = $(s.summaryContentSelector).html();
            window.console.log(summary);
            window.console.log(me.br2nl(summary));
            $(s.summaryContainerSelector).empty();
            s['summary_form_html'] = "<form id='edit-summary-form' method='POST' action='/edit_profile_summary'>";
            s['summary_form_html'] +=        "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'/>";
            s['summary_form_html'] +=            "<div class='form-group'>";
            s['summary_form_html'] +=                "<textarea rows='5' maxlength='300' name='summary' class='summary-textarea' placeholder='Write a short summary about yourself...'>";
            s['summary_form_html'] +=                    me.br2nl(summary); 
            s['summary_form_html'] +=                "</textarea>";
            s['summary_form_html'] +=            "</div>";
            s['summary_form_html'] +=        "<input type='submit' class='btn btn-default' value='Save' />";
            s['summary_form_html'] += "</form>";
            $(s.summaryContainerSelector).append(s.summary_form_html);
            me.bindEditSummaryFormAction();
        });
    };

    me.br2nl = function (str) {      
        str = str.replace(new RegExp("<br>", 'g'), "\r\n");
        str = str.replace(new RegExp("<p>", 'g'), "");
        str = str.replace(new RegExp("</p>", 'g'), "");
        return str;
    }

    return me;
}());