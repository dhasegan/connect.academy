$(function() {

    // (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    // (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    // m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    // })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

    // ga('create', 'UA-47744399-1', 'jcourse.herokuapp.com');
    // ga('send', 'pageview');

    // // For lazy loading images
    // $("img.course-image").lazyload({
    //     effect : "fadeIn"
    // });

    indexCourses = function(btn_studies) {
        var courses = $('.panel-course');
        var checked = $('.major-checkbox').filter( ':checked' );
        var allMajors = false;
        var allStudies = false;
        var searchTerm = $('.course-search-bar').val();
        if (checked.not( '#all-majors-cb' ).length == 0) {
            allMajors = true;
        }
        if (btn_studies == undefined && $('#st_Both').parent().hasClass('active')) {
            allStudies = true;
        }
        if (btn_studies != undefined && btn_studies == "Both") {
            allStudies = true
        }

        courses.each( function() {
            var show = true;
            classesArr = this.classList;
            if (!allMajors) {
                for(var i=0; i< classesArr.length; i++) {
                    if (classesArr[i].match('^major-') != undefined) {
                        major = classesArr[i].replace('major-', '');
                        if (!$('#checkbox_' + major).is(':checked')) {
                            show = false;
                        }
                    }
                }
            }
            if (show && !allStudies) {
                found = false;
                for(var i=0; i<classesArr.length; i++) {
                    if (classesArr[i].match('^studies-') != undefined) {
                        studies = classesArr[i].replace('studies-', '');
                        if (btn_studies == undefined && !$('#st_' + studies).parent().hasClass('active')) {
                            show = false;
                        }
                        if (btn_studies != undefined && btn_studies != studies) {
                            show = false;
                        }
                        found = true;
                    }
                }
                if (found == false) {
                    show = false;
                }
            }
            if (show) {
                credits = parseFloat( $(this).find('.course-credits').text() );
                values = $("#credit-slider").slider("values");
                if (credits < creditValues[values[0]] || credits > creditValues[values[1]]) {
                    show = false;
                }
            }
            if (show) {
                course_name = $(this).find('.course-name').find('a').text();
                if (course_name.indexOf(searchTerm) == -1) {
                    show = false;
                }
            }

            if (show) {
                $(this).parent().show();
            } else {
                $(this).parent().hide();
            }
        });

        $("img.course-image").lazyload({
            event : "click"
        });
        
    }

    // Search handle code!
    $(".course-search-bar").keypress(function(event) {
        if (event.which == 13) {
            indexCourses();
        }
    });
    $(".course-search-bar").keyup(function() {
        if ($(this).val() == "") {
            indexCourses();
        }
    });

    // Studies handle code!
    $('.btn-studies').click( function() {
        studies = $(this).children('.studies-radio')[0].id.replace('st_','')
        indexCourses(studies)
    });

    // Checkboxes handle code!
    majorCheckboxHandle = function() {
        if (this.id == "all-majors-cb") {
            $('.major-checkbox').prop('checked', false);
            $('#all-majors-cb').prop('checked', true);
        }
        var checked = $('.major-checkbox').filter( ':checked' );
        if (checked.length > 0) {
            if (checked.not( '#all-majors-cb' ).length > 0) {
                $('#all-majors-cb').prop('checked', false);
            }
        } else {
            $('#all-majors-cb').prop('checked', true);
        }

        indexCourses()
    }
    $('.major-checkbox').change(majorCheckboxHandle);

    // Credit slider handle code!
    var creditValues = [0.1, 0.15, 0.2, 0.3, 1.1, 2.5, 3.0, 3.75, 5.0, 7.5, 10.0, 12.0, 15.0, 30.0];
    var nrCredits = creditValues.length;

    function sliderStop(event, ui) {
        indexCourses()
    }
    function sliderChange(event, ui) {
        $("#slider-handle-0").val( creditValues[ ui.values[0] ] )
        $("#slider-handle-1").val( creditValues[ ui.values[1] ] )
    }
    $("#credit-slider").slider({
        orientation: "horizontal",
        range: true,
        max: nrCredits-1,
        values: [0, nrCredits-1],
        slide: sliderChange,
        stop: sliderStop
    });


    $("#slider-handle-0").val( creditValues[0] )
    $("#slider-handle-1").val( creditValues[creditValues.length - 1] )
    majorCheckboxHandle();

    // Activate Alerts
    $(".dismissable-alert").alert();
    // Email confirmation link
    $(".email-confirmation-link").click( function() {
        $.get($(this).attr("src"));
    });

    // Course page JS
    $('.rating-stars').raty( {
        starOn: '/static/images/star-on.png',
        starOff: '/static/images/star-off.png',
        starHalf: '/static/images/star-half.png',
        number: 5,
        mouseover: function(score, evt) {
            $(this).parents('form').find('.rating-my-score').text(score);
        },
        mouseout: function() {
            var form = $(this).parents('form');
            var score = form.find('input[name="old_score"]').val();
            form.find('.rating-my-score').text(score);
        },
        noRatedMsg: "To rate please log in!",
        score: function() {
            var form = $(this).parents('form');
            form.find('input[name="rating_value"]')
            return form.find('input[name="rating_value"]').val()
        },
        click: function(score, evt) {
            var form = $(this).parents('form');
            form.find('input[name="rating_value"]').val(score)
            var user = form.find('input[name="username"]')
            if (user.length > 0) {
                form.submit();
            }
        },
        readOnly: function() {
            var is_auth = $(this).parents('form').find('input[name="authenticated"]')
            return (is_auth.length == 0);
        },
        hints: ['1', '2', '3', '4', '5']
    });

    // Logged out rating tooltip
    var ratingTooltips = $('.ratings-tooltip')
    if (ratingTooltips.length > 0) {
        ratingTooltips.tooltip({
            placement: 'left',
            html: false,
            title: 'Log in to vote!'
        });
        ratingTooltips.attr('data-original-title', 'Log in to vote!')
    }
    var ratingClarif = $('.ratings-tooltip-clarif')
    if (ratingClarif.length > 0) {
        ratingClarif.tooltip({
            placement: 'top',
            title: function() {
                var type = $(this).parents('form').find('input[name="rating_type"]').val();
                if (type == 'ALL') {
                    return "How do you rate the course in general?"
                } else if (type == 'WKL') {
                    return "More stars means higher workload"
                } else if (type == 'DIF') {
                    return "More stars means higher difficulty"
                } else if (type == 'PRF') {
                    return "How do you rate this professor?"
                } 
            }
        })
    }

    // Tooltip for CampusNet
    $("#campusnet-popover").tooltip({title: 'Please log in with your CampusNet credentials!'});


    $("#email").blur(function(){
        var email_address = this.value;
        $.get('/university_by_email', {email: email_address},function(data,status) {
            if (data == "NotFound") {
                $("#email-ok").empty();
                $('#email-error').html("University Not Found");
            }
            else if (data == "Exists") {
                $("#email-ok").empty();
                $('#email-error').html("E-mail address exists");
            }
            else {
                // university found
                $("#email-error").empty();
                $('#email-ok').html(data);
            }
        });
    });

    $("#username").blur(function() {
        var username = this.value;
        $.get('/check_username', {username: username}, function(data,status) {
            if (data == "OK") {
                $("#username-error").empty();
                $("#username-ok").html("Username OK");
            }
            else {
                $("#username-ok").empty();
                $("#username-error").html(data);
            }

        });
    });

    $("#password, #password_confirmation").keyup(function() {
        var password = $("#password").val();
        var password_confirmation = $("#password_confirmation").val();

        if (password.length < 6) {
            $("#password-ok").empty();
            $("#password-error").html("Password is too short");
        }
        else {
            $("#password-ok").html("Password ok");
            $("#password-error").empty();
        }


        if (password_confirmation == password) {
            $("#password_confirmation-ok").html("Passwords match");
            $("#password_confirmation-error").empty();
        }
        else {
            $("#password_confirmation-ok").empty();
            $("#password_confirmation-error").html("Passwords do not match");
        }
    });
    


    $("#registration_form").submit(function(event) {
        var form = this;
        var fname = $("#fname").val();
        var lname = $("#lname").val();
        var password = $("#password").val();
        var password_confirmation = $("#password_confirmation").val();
        var username = $("#username").val();
        var email = $("#email").val();
        event.preventDefault();

        if (fname.length < 1 || lname.length < 1) {
            return false;
        }

        if (password.length < 6 || password != password_confirmation) {
            return false;
        }

        $.get('/validate_registration', {email: email, username:username},function(data,status) {
            if (data == "OK") {
                form.submit();
            }
        });  

    });
});

