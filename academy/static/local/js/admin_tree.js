var labelType, useGradients, nativeTextSupport, animate;

// $ is used by Javascrpt Infoviz Toolkit
jQuery( document ).ready(function() {

    AdminTree.init();

});

var AdminTree = (function() {
    var me = { 
        settings : {
            // Management form selectors

            //category forms
            categoryFormsSelector: ".category-forms",
            categoryNameSelector: ".category-forms form#edit-category-form input[name='name']",
            categoryIdSelector: ".category-forms form input[type='hidden'][name='cat_id']",
            registrationStatusSelector: ".category-forms form small[class='registration_deadline_status']",
            adminsContainerSelector: "#admins-form-container",
            // node styles
            categoryNotSelectedColor: "#0b56a8",
            categorySelectedColor: "#29ABE2",

            //course forms
            courseFormsSelector: ".course-forms",
            courseNameSelector: ".course-forms form#edit-course-form input[name='name']",
            courseIdSelector: ".course-forms form input[type='hidden'][name='course_id']",
            professorsContainerSelector: "#professors-form-container",
            //node styles
            courseSelectedColor: "#000",
            courseNotSelectedColor: "#444",

        },

        Log : {
            elem: false,
            write: function(text) {
                if (!this.elem) 
                this.elem = document.getElementById('log');
                this.elem.innerHTML = text;
                this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
            }
        },

        

    };

    var s; // short for settings
    var st = null;
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

    me.init = function() {
        (function() {
          var ua = navigator.userAgent,
              iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
              typeOfCanvas = typeof HTMLCanvasElement,
              nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
              textSupport = nativeCanvasSupport 
                && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
          //I'm setting this based on the fact that ExCanvas provides text support for IE
          //and that as of today iPhone/iPad current text support is lame
          labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
          nativeTextSupport = labelType == 'Native';
          useGradients = nativeCanvasSupport;
          animate = !(iStuff || !nativeCanvasSupport);
        })();

        s = this.settings;
        this.bindUIActions();
    };

    me.bindUIActions = function() {
        $(s.categoryFormsSelector + ", " + s.courseFormsSelector).on("submit", "form", function(event){
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

        
        st = new $jit.ST({
        //id of viz container element
        injectInto: 'infovis',
        //set duration for the animation
        duration: 800,
        //set animation transition type
        transition: $jit.Trans.Quart.easeInOut,
        //set distance between node and its children
        levelDistance: 50,

        levelsToShow: 1,
        //enable panning
        Navigation: {
          enable:true,
          panning:true
        },
        //set node and edge styles
        //set overridable=true for styling individual
        //nodes or edges
        Node: {
            width: 100,
            height:50 ,
            type: 'rectangle',
            color: '#0b56a8', 
            overridable:true
        },
        
        Edge: {
            type: 'bezier',
            overridable: true,
            color:'black'
        },
        
        onBeforeCompute: function(node){
            me.Log.write("loading " + node.name);
        },
        
        onAfterCompute: function(){
            me.Log.write("done");

        },
        
        //This method is called on DOM label creation.
        //Use this method to add event handlers and styles to
        //your node.
        onCreateLabel: function(label, node){
            label.id = node.id;            
            label.innerHTML = node.name;
            label.onclick = function(){
                st.onClick(node.id);
            };
            //set label styles
            var style = label.style;
            style.width = 60 + 'px';
            style.height = 17 + 'px';            
            style.cursor = 'pointer';
            style.color = 'white';
            style.fontSize = '0.8em';
            style.textAlign= 'center';
            style.paddingTop = '3px';
        },
        
        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            if (node.selected) {
                if (node.data.type == "category") {
                    node.data.$color = s.categorySelectedColor;
                    jQuery(s.courseFormsSelector).hide();
                    if (node.id != "root") {
                        jQuery(s.categoryFormsSelector).show();
                        // update the name field on the left container
                        jQuery(s.categoryNameSelector).val(node.name);
                        cat_id = node.id.split("-")[1];
                        // update all id fields in the category forms
                        jQuery(s.categoryIdSelector).val(cat_id);
                        // update the course registration deadline
                        jQuery(s.registrationStatusSelector).html(node.data.registration_deadline);
                        // update the list of admins
                        var admins = node.data.admins;
                        var length = admins.length;
                        jQuery(s.adminsContainerSelector).empty();
                        for (var i = 0; i < length; i++) {
                            var first_name = admins[i].first_name;
                            var last_name = admins[i].last_name;
                            var username = admins[i].username;
                            var admin_id = admins[i].id;
                            var own_admin = admins[i].own_admin;
                            var csrf = jQuery.cookie('csrftoken');
                            var cat_id = node.id.split("-")[1]
                            // create form
                            var form = "<li>"
                            form +=    "<form method='POST' action='admin_form_action' class = 'remove-admin'>";
                            form +=       "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf +"'/>";
                            form +=       "<input type='hidden' name='admin_id' value='" + admin_id + "'/>";
                            form +=       "<input type='hidden' name='cat_id' value='" + cat_id + "'/>";
                            form +=       "<input type='hidden' name='form_type' value = 'remove_admin'/>";
                            form +=       "<div class='form-group'>";
                            if (own_admin)
                                form +=         " <input type='submit' value='X' class='btn btn-danger btn-xs'/>";
                            form +=             " <a href='/profile/" + username + "'>" + first_name + " " + last_name + "</a>";
                            form +=       "</div>";
                            form +=    "</form>"
                            form +=    "</li>";
                            jQuery(s.adminsContainerSelector).append(form);
                        }
                    }
                    else {
                        jQuery(s.categoryFormsSelector).hide();
                        jQuery(s.courseFormsSelector).hide();
                    }
                        
                }
                else if (node.data.type == "course") {
                    node.data.$color = s.courseSelectedColor;
                    jQuery(s.categoryFormsSelector).hide();
                    jQuery(s.courseFormsSelector).show();
                    jQuery(s.courseNameSelector).val(node.name);
                    course_id = node.id.split("-")[1];
                    // update all id fields in the category forms
                    jQuery(s.courseIdSelector).val(course_id);
                    var profs = node.data.professors;
                    var length = profs.length;
                    jQuery(s.professorsContainerSelector).empty();
                    for (var i = 0; i < length; i++) {
                        var first_name = profs[i].first_name;
                        var last_name = profs[i].last_name;
                        var username = profs[i].username;
                        var prof_id = profs[i].id;
                        var csrf = jQuery.cookie('csrftoken');
                        var course_id = node.id.split("-")[1]
                        // create form
                        var form = "<li>"
                        form +=    "<form method='POST' action='admin_form_action' class ='remove-professor'>";
                        form +=       "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf +"'/>";
                        form +=       "<input type='hidden' name='professor_id' value='" + prof_id + "'/>";
                        form +=       "<input type='hidden' name='form_type' value = 'remove_professor'/>";
                        form +=       "<input type='hidden' name='course_id' value = '" + course_id + "'/>"
                        form +=       "<div class='form-group'>";
                        form +=             " <input type='submit' value='X' class='btn btn-danger btn-xs'/>";
                        form +=             " <a href='/profile/" + username + "'>" + first_name + " " + last_name + "</a>";
                        form +=       "</div>";
                        form +=    "</form>"
                        form +=    "</li>";
                        jQuery(s.professorsContainerSelector).append(form);
                    }
                }
                    
            }
            else {
                if (node.data.type == "category") {
                    node.data.$color = s.categoryNotSelectedColor;
                }
                else if (node.data.type == "course") {
                    node.data.$color = s.courseNotSelectedColor;
                }
            }
            
        },
        
        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {

                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    //load json data
    st.loadJSON(json);
    //compute node positions and layout
    st.compute();
    //optional: make a translation of the tree
    st.geom.translate(new $jit.Complex(-200, 0), "current");
    //emulate a click on the root node.
    st.onClick(st.root);
    //end   
    };


    return me;
}());

