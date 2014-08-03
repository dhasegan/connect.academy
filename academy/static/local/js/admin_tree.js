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

