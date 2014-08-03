jQuery( document ).ready(function( $ ) {

    ConnectGlobal.init();

    if ($('.explore-page').length > 0) { ExplorePage.init(); }
    else if ($('.course-page').length > 0) { CoursePage.init(); ForumPage.init(); }
    else if ($('.forum-page').length > 0) { ForumPage.init(); }
    else if ($('.welcome-page').length > 0) { WelcomePage.init(); }
});

var ConnectGlobal = (function() {
    var me = { 
        settings: {
            dismissableAlerts: $(".dismissable-alert"),
            emailConfirmationLinks: $(".email-confirmation-link"),
            campusnetPopover: $("#campusnet-popover"),
        }
    }, s;

    me.init = function() {
        s = this.settings;

        this.bindUIActions();
    };

    me.bindUIActions = function() {
        // Activate Alerts
        s.dismissableAlerts.alert();
        // Email confirmation link
        s.emailConfirmationLinks.click( function() {
            $.get($(this).attr("src"));
        });

        // Tooltip for CampusNet
        s.campusnetPopover.tooltip({title: 'Please log in with your CampusNet credentials!'});
    };

    return me;
}());

// ****************************************************
// TODO: Break the code below into separate files
//
jQuery( document ).ready(function( $ ) {


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

    // Forum register form
    $('.forumregistration-form').submit(function(event) {
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
    $('.forumregistration-form').submit(function(event) {
        SubmitFormAjax(event, this,
            function(result) {
                $(".forum-management").html(result.html)
            }, 
            function(jqXHR, textStatus, errorThrown) {
                $(".forum-management").html(textStatus)
            }
        );
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
                    /**********************************************/
                    /* No matter which form, show success message */
                    /**********************************************/
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
                                if (parent.isDescendantOf(node.id) ||
                                    parent.id == node.id) {
                                    st.graph.removeAdjacence(cat_id,node.id);
                                    st.graph.addAdjacence(old_parent,node);
                                }

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