jQuery( document ).ready(function( $ ) { 

    // For lazy loading images
    $("img.course-image").lazyload({
        effect : "fadeIn"
    });

    getAvoidedCategoriesIds = function() {
        var $checked = $('.cb-normal').filter(':checked');
        var $avoided = $([]);
        $checked.each( function() {
            $bad_categories = $(this).parents('.category-checkbox').find('.cb-normal').not(':checked');
            $bad_ids = $bad_categories.map( function() { return this.name; } )
            $avoided = $avoided.add($bad_ids)
        });
        return $avoided.toArray();
    }

    indexCourses = function() {
        var courses = $('.course-panel');

        var searchTerm = $('.course-search-bar').val();
        var avoided_categories = getAvoidedCategoriesIds();

        courses.each( function() {
            var show = true;
            classesArr = this.classList;
            if (show) {
                $(classesArr).each( function() {
                    if (this.indexOf('ct-') >= 0) {
                        var category_id = this.replace("ct-", "");
                        if (avoided_categories.indexOf(category_id) >= 0) {
                            show = false;
                        }   
                    }
                })
            }
            if (show) {
                var credits = parseFloat( $(this).find('.course-credits').text() );
                var values = $("#credit-slider").slider("values");
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
                indexCourses()
            },
            error: function() {
            }
        });

    }
    $('.cat-cb').change(categoryCheckboxHandle)

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

    indexCourses()
});