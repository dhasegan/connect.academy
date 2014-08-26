var ProfilePage = (function() {
    var me = { 
        settings: {
            editSummaryFormSelector: "#edit-summary-form",
            summaryContainerSelector: ".profile-summary"

        }
    }, s;

    me.init = function() {
        s = this.settings;

        this.bindUIActions();
    };


    me.bindUIActions = function() {
        
    };

    return me;
}());