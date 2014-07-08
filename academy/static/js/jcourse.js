$.noConflict();
jQuery( document ).ready(function( $ ) { 

    // (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    // (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    // m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    // })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

    // ga('create', 'UA-47744399-1', 'jcourse.herokuapp.com');
    // ga('send', 'pageview');

    // For lazy loading images
    $("img.course-image").lazyload({
        effect : "fadeIn"
    });

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

    // Datetimepicker and Time handlers
    $('.homework-start-datetime').datetimepicker({
        defaultDate: moment().startOf("hour"),
        minDate: moment(),
        maxDate: moment().add("years", 1),
        pick12HourFormat: false
    });
    $('.homework-deadline-datetime').datetimepicker({
        defaultDate: moment().add("weeks", 1).endOf("day"),
        minDate: moment(),
        maxDate: moment().add("years", 1),
        pick12HourFormat: false
    });
    $('.homework-datetime-input').click(function() {
        var $parent = $(this.parentNode);
        var $button = $parent.find(".homework-datetime-button");
        $button.parent().data("DateTimePicker").show();
    });
    $('.homework-form').ready(function() {
        var tz = $(this).find('input[name="timezone"]');
        tz.val( moment().zone() )
    });

    function SubmitFormAjax(event, form, successFunction, errorFunction) {
        event.preventDefault();
        $.ajax({
            type: form.method,
            url: form.action,
            data: $(form).serialize(),
            success: successFunction,
            error: errorFunction
        });
    };

    // Forum register form
    $('.forumcourseregistration-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                $(".forum-management").html(result.html)
            }, 
            function(jqXHR, textStatus, errorThrown) {
                $(".forum-management").html(textStatus)
            }
        );
    });

    // Get reply form for forum answer reply
    $('.forumcourseregistration-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                $(".forum-management").html(result.html)
            }, 
            function(jqXHR, textStatus, errorThrown) {
                $(".forum-management").html(textStatus)
            }
        );
    });

    // Post new answer in the forum
    $('.forumpostnewanswer-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                var $answer_tab = $(result.id_selector);
                $answer_tab.html(result.html);
            }, 
            function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus)
            }
        );
    });

    $('.getreplyform-link').click(function(event) {
        event.preventDefault();
        var $link = $(this);
        var $reply_form = $link.parents('.answer-footer').find('.reply-form');
        if (!($reply_form.hasClass('active'))) {
            $.ajax({
                type: "get",
                url: this.href,
                success: function(response) {
                    $reply_form.html(response.html).slideDown();
                    $reply_form.addClass('active')
                }
            })
        }
    });

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

    // Confirm the registration of a student for a course. 
    $(".confirm_registration").submit(function(event) {
        var form = $(this);
        var data = form.serialize();
        var courseID = $("[name='courseID']", form).val();
        event.preventDefault();
        $.ajax({
            'url': form.attr('action'),
            'type': "POST",
            'data': data,
            'success': function(data) {
                if (data == "OK") {
                    $('#register_button' + courseID).text('Pending Registration...'); 
                    $('#register_button' + courseID).attr('disabled',true);   
                    $("#registrationModal"+courseID).modal('hide');                   
                }
            }
        });
    });

    $(".send-mass-email-form").submit(function(event) {
        var form = $(this);
        var data = form.serialize();
        var courseID = $("#course",form).val();
        var success_div_id = "email-success" + courseID;
        var error_div_id = "email-error" + courseID;
        event.preventDefault();
        var checkedAtLeastOne = false;
        $('input[type="checkbox"]',form).each(function() {
            if ($(this).is(":checked")) {
                checkedAtLeastOne = true;
            }
        });
        if (checkedAtLeastOne) {
            $.ajax({
                'url': form.attr('action'),
                'type': 'POST',
                'data': data,
                'success': function(data) {
                    if (data == "OK") {
                        $('.email-success',form).show();
                        $('.email-success',form).html('Your email was sent!');
                        $('.email-success',form).delay(2000).fadeOut(300);
                    }
                    else {
                        $('.email-error',form).show();
                        $('.email-error',form).html(data);
                        $('.email-error',form).delay(3000).fadeOut(300);
                    }
                }
            });
        }
        else {
            $('.email-error',form).show();
            $('.email-error',form).html("Please select at least one recepient.");
            $('.email-error',form).delay(2000).fadeOut(300);
        }
    });

    $('.selectAll').click(function(event) {   
        if(this.checked) {
        // Iterate each checkbox
            $(this).parent().parent().find("input[type='checkbox']").each(function() {
                this.checked = true;                        
            });
        }
        else {
            $(this).parent().parent().find("input[type='checkbox']").each(function() {
                this.checked = false;                        
            });
        }
    });

    function findById(json_tree, id) {
        if (json_tree.id == id) {
            return json_tree;
        }
        else {
            for (var i = 0; i < json_tree.children.length; i++) {
                node = json_tree.children[i];
                result = findById(node,id);
                if (result != null)
                    return result; 
            }
            return null;
        }
    }
    // add the admin in the tree object
    function addAdminToSubtree(node,admin) {
        if (node.data.type == "category") {
            node.data.admins.push(admin);
            var new_admin = jQuery.extend({}, admin);
            new_admin.own_admin = false;
            node.eachSubnode(function(node) {
                addAdminToSubtree(node, new_admin);
            });
        }
           
    }
    function removeAdminFromSubtree(node,admin_id) {
        if (node.data.type == 'category') {
            for (var i = 0; i < node.data.admins.length; i++) {
                if (node.data.admins[i].id == admin_id) {
                    node.data.admins.splice(i,1);
                    break;
                }
            }
            node.eachSubnode(function(node) {
                removeAdminFromSubtree(node, admin_id);
            });
        } 
    }
    $(".category-forms, .course-forms").on("submit", "form", function(event){
        var form = $(this);
        var data = form.serialize();
        event.preventDefault();
        $.ajax({
            'dataType': "json",
            'url' : form.attr('action'),
            'type': 'POST',
            'data': data,
            'success': function(data) {
                var status = data.status;
                var message = data.message;
                if (status == "OK") {
                    $('.text-success',form).show();
                    $('.text-success',form).html(message);
                    $('.text-success',form).delay(4000).fadeOut(400);
                    // Make the UI changes for specific forms. 

                    /*************************************/
                    /********** CATEGORY FORMS ***********/
                    /*************************************/
                    if ($(form).hasClass('remove-admin')) {
                        // remove admin form
                        form.fadeOut(400);
                        var cat_id = data.data.cat_id;
                        var admin_id = data.data.admin_id;
                        var node = st.graph.getNode("category-" + cat_id);
                        removeAdminFromSubtree(node,admin_id);
                    }
                    else if (form.attr("id") == "edit-category-form") {
                        // change name form
                        var cat_id = data.data.cat_id;
                        var new_name = data.data.new_name;
                        var node = st.graph.getNode("category-" + cat_id);
                        node.name = new_name; // change the name in the tree object
                        $("#category-"+cat_id).html(new_name); // change it in the UI
                    }
                    else if (form.attr("id") == "new-admin-form") {
                        // new admin form
                        var cat_id = data.data.cat_id;
                        var admin_fname = data.data.admin_fname;
                        var admin_lname = data.data.admin_lname;
                        var admin_name = admin_fname + " " + admin_lname;
                        var admin_username = data.data.admin_username;
                        var admin_id = data.data.admin_id;
                        var csrf = jQuery.cookie('csrftoken');
                        // create form
                        var admin_form = "<li>"
                        admin_form +=    "<form method='POST' action='admin_form_action' class = 'remove-admin'>";
                        admin_form +=       "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf +"'/>";
                        admin_form +=       "<input type='hidden' name='admin_id' value='" + admin_id + "'/>";
                        admin_form +=       "<input type='hidden' name='cat_id' value='" + cat_id + "'/>";
                        admin_form +=       "<input type='hidden' name='form_type' value = 'remove_admin'/>";
                        admin_form +=       "<div class='form-group'>";
                        admin_form +=             " <input type='submit' value='X' class='btn btn-danger btn-xs'/>";
                        admin_form +=             " <a href='/profile/" + admin_username + "'>" + admin_name + "</a>";
                        admin_form +=       "</div>";
                        admin_form +=    "</form>"
                        admin_form +=    "</li>";
                        jQuery("#admins-form-container").append(admin_form);


                        admin = {
                            'first_name': admin_fname,
                            'last_name': admin_lname,
                            'username': admin_username,
                            'id': admin_id,
                            'own_admin': true
                        }
                        
                        node = st.graph.getNode('category-'+cat_id);
                        addAdminToSubtree(node,admin);
                    }
                    else if (form.attr("id") == "new-category-form") {
                        var cat_id = data.data.cat_id;
                        var parent_id = data.data.parent_id;
                        var cat_name = data.data.cat_name;
                        var parent_node = st.graph.getNode('category-'+parent_id);
                        var new_node = {
                                            'id' : "category-" + cat_id,
                                            'name' : cat_name,
                                            'data' : {
                                                'type': 'category',
                                                'admins': []
                                            }
                                        }
                        var child = st.graph.addNode(new_node);
                        st.graph.addAdjacence(parent_node, child, {});
                        st.refresh();
                    }
                    else if (form.attr("id") == "move-course-form") {
                        var cat_id = 'category-' + data.data.cat_id;
                        var course_id = 'course-' + data.data.course_id;
                        var course_node = st.graph.getNode(course_id);
                        var parent  = course_node.getParents()[0];
                        var new_cat = st.graph.getNode(cat_id);
                        if (parent) {
                            st.graph.removeAdjacence(parent.id,course_node.id);
                        }
                        st.graph.addAdjacence(new_cat,course_node);
                        course_node.data.type = "course";
                        st.refresh();                        
                    }
                    else if (form.attr("id") == "delete-category-form") {
                        var cat_id = 'category-' + data.data.cat_id;
                        var delete_all = data.data.delete_all;
                        parent = st.graph.getNode(cat_id).getParents()[0];
                        if (delete_all) {
                            st.removeSubtree(cat_id,true,'animate', {
                                onComplete: function() {
                                    st.onClick(parent.id);
                                    st.refresh();   
                                }
                            });
                        }
                        else {
                            var cat = st.graph.getNode(cat_id);
                            cat.eachSubnode(function(node) {
                                st.graph.addAdjacence(parent,node);
                            });
                            st.graph.removeNode(cat_id);
                            $('#'+cat_id).hide();
                            st.onClick(parent.id);
                            st.refresh();        
                        }
                    } 

                    else if (form.attr("id") == "move-category-form") {
                        var cat_id = 'category-' + data.data.cat_id;
                        var parent_id = 'category-' + data.data.parent_id;
                        var category = st.graph.getNode(cat_id);
                        var parent = st.graph.getNode(parent_id);
                        var old_parent = category.getParents()[0];
                        var is_descendant = data.data.descendant;
                        if (is_descendant) {
                            category.eachSubnode(function(node) {
                                st.graph.removeAdjacence(cat_id,node.id);
                                st.graph.addAdjacence(old_parent,node);
                            });
                        }
                        st.graph.removeAdjacence(old_parent.id,cat_id);
                        st.graph.addAdjacence(parent,category,{});
                        st.refresh();
                    }

                    /*************************************/
                    /********** COURSE FORMS *************/
                    /*************************************/
                    else if (form.attr("id") == "edit-course-form") {
                        // change name form
                        var course_id = data.data.course_id;
                        var new_name = data.data.course_name;
                        var node = st.graph.getNode("course-" + course_id);
                        node.name = new_name; // change the name in the tree object
                        $("#course-"+course_id).html(new_name); // change it in the UI
                    }
                    else if (form.attr("id") == "new-prof-form") {
                        var course_id = data.data.course_id;
                        var prof_fname = data.data.professor_fname;
                        var prof_lname = data.data.professor_lname;
                        var prof_name = prof_fname + " " + prof_lname;
                        var prof_username = data.data.professor_username;
                        var prof_id = data.data.professor_id;
                        var csrf = jQuery.cookie('csrftoken');
                        // create form
                        var prof_form = "<li>"
                            prof_form +=    "<form method='POST' action='admin_form_action' class ='remove-professor'>";
                            prof_form +=       "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf +"'/>";
                            prof_form +=       "<input type='hidden' name='professor_id' value='" + prof_id + "'/>";
                            prof_form +=       "<input type='hidden' name='form_type' value = 'remove_professor'/>";
                            prof_form +=       "<input type='hidden' name='course_id' value = '" + course_id + "'/>"
                            prof_form +=       "<div class='form-group'>";
                            prof_form +=             " <input type='submit' value='X' class='btn btn-danger btn-xs'/>";
                            prof_form +=             " <a href='/profile/" + prof_username + "'>" + prof_name + "</a>";
                            prof_form +=       "</div>";
                            prof_form +=    "</form>"
                            prof_form +=    "</li>";
                            jQuery("#professors-form-container").append(prof_form);


                        professor = {
                            'first_name': prof_fname,
                            'last_name': prof_lname,
                            'username': prof_username,
                            'id': prof_id
                        }
                        
                        node = st.graph.getNode('course-'+course_id);
                        node.data.professors.push(professor);
                    }
                    else if (form.attr("id") == "move-to-category-form") {
                        var cat_id = 'category-' + data.data.cat_id;
                        var course_id = 'course-' + data.data.course_id;
                        var course_node = st.graph.getNode(course_id);
                        var parent  = course_node.getParents()[0];
                        var new_cat = st.graph.getNode(cat_id);
                        if (parent) {
                            st.graph.removeAdjacence(parent.id,course_node.id);
                        }
                        st.graph.addAdjacence(new_cat,course_node);
                        st.refresh();
                    }
                    else if ($(form).hasClass('remove-professor')) {
                        // remove admin form
                        form.fadeOut(400);
                        var course_id = "course-" + data.data.course_id;
                        var prof_id = data.data.professor_id;
                        var node = st.graph.getNode(course_id);
                        for (var i = 0; i < node.data.professors.length; i++) {
                            if (node.data.professors[i].id == prof_id) {
                                node.data.professors.splice(i,1);
                                break;
                            }

                        }
                    }
                    else if (form.attr("id") == "delete-course-form") {
                        var course_id = 'course-' + data.data.course_id;
                        parent = st.graph.getNode(course_id).getParents()[0]; 
                        st.removeSubtree(course_id,true,'animate', {
                            onComplete: function() {
                                st.onClick(parent.id);
                                st.refresh();   
                            }
                        });
                        
                    }
                }
                else if (status == "Warning") {
                    $('.text-warning',form).show();
                    $('.text-warning',form).html(message);
                    $('.text-warning',form).delay(4000).fadeOut(400);
                }
                else if (status == "Error") {
                    $('.text-danger',form).show();
                    $('.text-danger',form).html(message);
                    $('.text-danger',form).delay(4000).fadeOut(400);
                }

                
                       
            }
        });
    });
    
    
});