jQuery( document ).ready(function( $ ) { 

    // For lazy loading images
    $("img.course-image").lazyload({
        effect : "fadeIn"
    });

    indexCourses = function(btn_studies) {
        var courses = $('.course-panel');
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

    // Category Checkbox All-vs-normal
    categoryCheckboxHandle = function() {
        var $this = $(this)
        var $parent = $this.parents('.category-checkbox');
        var $cb_all = $parent.find('.cb-all');

        if ($this.hasClass('cb-all')) {
            $parent.find('.cb-normal').prop('checked', false);
            $cb_all.prop('checked', 'true');
        }
        var $checked = $parent.find('.cat-cb').filter( ':checked' );
        if ($checked.length > 0) {
            if ($checked.not('.cb-all').length > 0) {
                $cb_all.prop('checked', false);
            }
        } else {
            $cb_all.prop('checked', true);
        }

        var $form = $this.parents('.categories-form');
        $.ajax({
            type: $form[0].method,
            url: $form[0].action,
            data: $form.serialize(),
            success: function(result) {
                $(".explore_categories").html(result.html)
                $('.cat-cb').change(categoryCheckboxHandle)
            },
            error: function() {
            }
        });

    }
    $('.cat-cb').change(categoryCheckboxHandle)


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

});