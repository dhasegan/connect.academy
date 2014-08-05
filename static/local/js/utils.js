var Utils = {
    SubmitFormAjax: function(event, form, successFunction, errorFunction) {
        if (event)
            event.preventDefault();
        $.ajax({
            type: form.method,
            url: form.action,
            data: $(form).serialize(),
            success: successFunction,
            error: errorFunction
        });
    }
};