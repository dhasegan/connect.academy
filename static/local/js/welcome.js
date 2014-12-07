var WelcomePage = (function() {
    var me = { 
        settings: {
            registrationFormSelector: "#registration_form",
            registerModal: $('#register_modal'),
            signupErrors: $('.signup-errors'),

            firstNameSelector: "#fname",
            lastNameSelector: "#lname",
            
            usernameSelector: "#username",
            usernameSuccessSelector: "#username-ok",
            usernameErrorSelector: "#username-error",

            emailSelector: "#email",
            emailSuccessSelector: "#email-ok",
            emailErrorSelector: "#email-error",

            
            passwordSelector: "#password",
            passwordSuccessSelector: "#password-ok",
            passwordErrorSelector: "#password-error",


            passwordConfirmationSelector: "#password_confirmation",
            passwordConfirmationSuccessSelector: "#password_confirmation-ok",
            passwordConfirmationErrorSelector: "#password_confirmation-error",
        
            universityByEmailLink:'/university_by_email',
            checkUsernameLink: '/check_username',
            validateRegistrationLink: '/validate_registration'
        }
    }, s;

    me.init = function() {
        s = this.settings;

        if (s.signupErrors.length > 0) {
            s.registerModal.modal('show');
        }

        this.bindUIActions();
    };

    me.bindUIActions = function() {
        $(s.emailSelector).blur(function(){
            var email_address = this.value;
            $.get(s.universityByEmailLink, {email: email_address},function(data,status) {
                data = $.parseJSON(data);
                if (data.status == "Error") {
                    $(s.emailSuccessSelector).empty();
                    $(s.emailErrorSelector).html(data.message);
                }
                else if (data.status == "OK") {
                    // university found
                    $(s.emailErrorSelector).empty();
                    $(s.emailSuccessSelector).html(data.message);
                }
            });
        });

        $(s.usernameSelector).blur(function() {
            var username = this.value;
            $.get(s.checkUsernameLink, {username: username}, function(data,status) {
                data = $.parseJSON(data);
                if (data.status == "OK") {
                    $(s.usernameErrorSelector).empty();
                    $(s.usernameSuccessSelector).html(data.message);
                }
                else if (data.status == "Error") {
                    $(s.usernameSuccessSelector).empty();
                    $(s.usernameErrorSelector).html(data.message);
                }

            });
        });

        $(s.passwordSelector + ", " + s.passwordConfirmationSelector).keyup(function() {
            var password = $(s.passwordSelector).val();
            var password_confirmation = $(s.passwordConfirmationSelector).val();

            if (password.length < 6) {
                $(s.passwordSuccessSelector).empty();
                $(s.passwordErrorSelector).html("Password is too short");
            }
            else {
                $(s.passwordSuccessSelector).html("Password ok");
                $(s.passwordErrorSelector).empty();
            }


            if (password_confirmation == password) {
                $(s.passwordConfirmationSuccessSelector).html("Passwords match");
                $(s.passwordConfirmationErrorSelector).empty();
            }
            else {
                $(s.passwordConfirmationSuccessSelector).empty();
                $(s.passwordConfirmationErrorSelector).html("Passwords do not match");
            }
        });



        $(s.registrationFormSelector).submit(function(event) {
            var form = this;
            var fname = $(s.firstNameSelector).val();
            var lname = $(s.lastNameSelector).val();
            var password = $(s.passwordSelector).val();
            var password_confirmation = $(s.passwordConfirmationSelector).val();
            var username = $(s.usernameSelector).val();
            var email = $(s.emailSelector).val();
            event.preventDefault();

            if (fname.length < 1 || lname.length < 1) {
                return false;
            }

            if (password.length < 6 || password != password_confirmation) {
                return false;
            }

            $.get(s.validateRegistrationLink, {email: email, username:username},function(data,status) {
                data = $.parseJSON(data);
                if (data.status == "OK") {
                    form.submit();
                }
            });

        });
        
    };

    return me;
}());





