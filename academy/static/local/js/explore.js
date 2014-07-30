jQuery( document ).ready(function( $ ) { 

    /*************************************
        Lazy load images
    **************************************/
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

    /*************************************
        Index the courses in the sequence
    **************************************/
    indexCourses = function() {
        var courses = $('.course-panel');

        var searchTerm = $('.course-search-bar').val();
        var avoided_categories = getAvoidedCategoriesIds();

        var creditsCurrentValues = $("#credits-slider").slider("values");
        var ratingsCurrentValues = $("#ratings-slider").slider("values");

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
                if (credits < creditsValues[creditsCurrentValues[0]] ||
                    credits > creditsValues[creditsCurrentValues[1]]) {
                        show = false;
                }
            }
            if (show) {
                var rating = 0.0;
                var rating_item = $(this).find('.course-rating');
                if (rating_item.length > 0) {
                    rating = parseFloat( rating_item.text() );
                }
                if ((ratingsCurrentValues[0] > 0 && rating < ratingsValues[ratingsCurrentValues[0]]) ||
                    (ratingsCurrentValues[1] > 0 && rating > ratingsValues[ratingsCurrentValues[1]])) {
                        show = false;
                }
                if (ratingsCurrentValues[1] == 0 && rating > 0) {
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

    /*************************************
        Search handle code!
    **************************************/
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

    /*************************************
        Category Checkbox All-vs-normal
    **************************************/
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


    /*************************************
        Sliders handle code!
    **************************************/
    function sliderStop(event, ui) {
        indexCourses()
    }

    /*************************************
        Credit slider handle code!
    **************************************/
    // input: creditsValues - as the values of the credits
    var nrCredits = creditsValues.length;

    function creditsSliderChange(event, ui) {
        $("#credits_handle_0").val( creditsValues[ ui.values[0] ] )
        $("#credits_handle_1").val( creditsValues[ ui.values[1] ] )
    }
    $("#credits-slider").slider({
        orientation: "horizontal",
        range: true,
        max: nrCredits-1,
        values: [0, nrCredits-1],
        slide: creditsSliderChange,
        stop: sliderStop
    });
    $("#credits_handle_0").val( creditsValues[0] )
    $("#credits_handle_1").val( creditsValues[creditsValues.length - 1] )


    /*************************************
        Ratings slider handle code!
    **************************************/
    ratingsValues = ["Unrated", 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5]
    var nrRatings = ratingsValues.length;

    function ratingsSliderChange(event, ui) {
        $("#ratings_handle_0").val( ratingsValues[ ui.values[0] ] )
        $("#ratings_handle_1").val( ratingsValues[ ui.values[1] ] )
    }
    $("#ratings-slider").slider({
        orientation: "horizontal",
        range: true,
        max: nrRatings-1,
        values: [0, nrRatings-1],
        slide: ratingsSliderChange,
        stop: sliderStop
    });
    $("#ratings_handle_0").val( ratingsValues[0] )
    $("#ratings_handle_1").val( ratingsValues[ratingsValues.length - 1] )

    // Index courses
    indexCourses()
});