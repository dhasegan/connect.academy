var HomeworkDashboard = (function() {
    var me = {
        settings: {
            // Homework details edit
            homeworkStartDatetime: $('.homework-start-datetime'),
            homeworkDeadlineDatetime: $('.homework-deadline-datetime'),
            homeworkDatetimeInput: $('.homework-datetime-input'),
            homeworkForm: $('.homework-form'),

            // Main form
            graderFormSelector: '.grader-form',

            // Interact buttons
            saveButton: $('.save-btn'),
            savePublishButton: $('.save-publish-btn'),
            publishHwSubmitButton: $('.publish-hw-submit'),

            hwSaveSelector: '.hw-save',
            hwNotReadySelector: '.hw-notready',

            // Inputs
            inputSaveSelector: 'input[name="save"]',
            inputPublishSelector: 'input[name="publish"]',
            inputGradeSelector: '.grade-input',
        }
    }, s;

    me.init = function() {
        s = me.settings;

        // Datetimepicker and Time handlers
        s.homeworkStartDatetime.datetimepicker({
            minDate: moment().subtract("months", 1),
            maxDate: moment().add("years", 1),
            pick12HourFormat: false
        });
        s.homeworkDeadlineDatetime.datetimepicker({
            minDate: moment().subtract("months", 1),
            maxDate: moment().add("years", 1),
            pick12HourFormat: false
        });

        this.bindUIActions();
    };

    me.bindUIActions = function() {
        s.homeworkDatetimeInput.click(function() {
            var $parent = $(this.parentNode);
            var $button = $parent.find(".homework-datetime-button");
            $button.parent().data("DateTimePicker").show();
        });
        s.homeworkForm.ready(function() {
            var tz = $(this).find('input[name="timezone"]');
            tz.val( moment().zone() );
        });

        s.saveButton.click(this.setSaveInput);
        s.savePublishButton.click(this.savePublishAction);
        s.publishHwSubmitButton.click(this.publishHwSubmit)
    };

    me.publishHwSubmit = function() {
        formSelector = $(this).attr('form-id-selector');
        $(formSelector).submit();
    }

    me.savePublishAction = function(event) {
        event.preventDefault();
        me.setSavePublishInput(this);
        $form = $(this).parents(s.graderFormSelector);
        if ( me.canPublish($form) ) {
            $form.find(s.hwSaveSelector).removeClass('hidden');
            $form.find(s.hwNotReadySelector).addClass('hidden');
        } else {
            $form.find(s.hwSaveSelector).addClass('hidden');
            $form.find(s.hwNotReadySelector).removeClass('hidden');
        }
    };

    me.setSaveInput = function(event) {
        $form = $(this).parents(s.graderFormSelector);
        $form.find(s.inputPublishSelector).val('');
    };

    me.setSavePublishInput = function(btn) {
        $form = $(btn).parents(s.graderFormSelector);
        $form.find(s.inputPublishSelector).val('True');
    }

    me.canPublish = function($form) {
        var canPublish = true;
        var inputs = $form.find(s.inputGradeSelector);
        inputs.each(function() {
            if ($(this).val() === "") {
                canPublish = false;
            }
        });
        return canPublish;
    }

    return me;
}());
