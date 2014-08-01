ExplorePage = (function () {
    var me = {
        settings: {
            // -- Sidebar --
            // Searchbar
            searchBar: $(".course-search-bar"),

            // Categories
            categoryCheckboxSelector: ".cat-cb",
            checkboxAllSelector: ".cb-all",
            checkboxNormalSelector: ".cb-normal",
            categoryCheckboxWrapperSelector: ".category-checkbox",
            categoriesSearchWrapper: $(".explore_categories"),

            // Credits
            creditsSlider: $("#credits-slider"),
            creditsHandle0: $("#credits_handle_0"),
            creditsHandle1: $("#credits_handle_1"),
            creditsValues: creditsValues,
            nrCredits: creditsValues.length,

            // Ratings
            ratingsSlider: $("#ratings-slider"),
            ratingsHandle0: $("#ratings_handle_0"),
            ratingsHandle1: $("#ratings_handle_1"),
            ratingsValues: ["Unrated", 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5],
            nrRatings: 42,

            // -- Course sequence --
            coursePanelSelector: ".course-panel",
            courseCreditsSelector: ".course-credits",
            courseRatingsSelector: ".course-rating",
            courseNameSelector: ".course-name",
            courseImageSelector: "img.course-image",
        }
    }, s;

    me.init = function() {
        s = this.settings;

        // Credits handle
        s.creditsSlider.slider({
            orientation: "horizontal",
            range: true,
            max: s.nrCredits-1,
            values: [0, s.nrCredits-1],
            slide: this.creditsSliderChange,
            stop: this.sliderStop
        });
        s.creditsHandle0.val( s.creditsValues[0] );
        s.creditsHandle1.val( s.creditsValues[s.nrCredits - 1] );

        // Ratings handle
        s.ratingsSlider.slider({
            orientation: "horizontal",
            range: true,
            max: s.nrRatings-1,
            values: [0, s.nrRatings-1],
            slide: this.ratingsSliderChange,
            stop: this.sliderStop
        });
        s.ratingsHandle0.val( s.ratingsValues[0] );
        s.ratingsHandle1.val( s.ratingsValues[s.nrRatings - 1] );

        // Index courses
        this.indexCourses();

        // Bind actions
        this.bindUIActions();
    };

    me.bindUIActions = function() {
        // Lazy load images
        $(s.courseImageSelector).lazyload({
            effect: "fadeIn",
        });

        // Search handle
        s.searchBar.keypress(function(event) {
            // on enter
            if (event.which == 13) {
                ExplorePage.indexCourses();
            }
        });
        s.searchBar.keyup(function() {
            // on empty
            if ($(this).val() == "") {
                ExplorePage.indexCourses();
            }
        });

        // Category handle
        $(s.categoryCheckboxSelector).change(this.categoryCheckboxHandle);
    };

    me.getAvoidedCategoriesIds = function() {
        var $checked = $(s.checkboxNormalSelector).filter(':checked');
        var $avoided = $([]);
        $checked.each( function() {
            $bad_categories = $(this).parents(s.categoryCheckboxWrapperSelector).find(s.checkboxNormalSelector).not(':checked');
            $bad_ids = $bad_categories.map( function() { return this.name; } )
            $avoided = $avoided.add($bad_ids)
        });
        return $avoided.toArray();
    };

    /*************************************
        Index the courses in the sequence
    **************************************/
    me.indexCourses = function() {
        var courses = $(s.coursePanelSelector);

        var searchTerm = s.searchBar.val();
        var avoided_categories = this.getAvoidedCategoriesIds();

        var creditsCurrentValues = s.creditsSlider.slider("values");
        var ratingsCurrentValues = s.ratingsSlider.slider("values");

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
                var credits = parseFloat( $(this).find(s.courseCreditsSelector).text() );
                if (credits < s.creditsValues[creditsCurrentValues[0]] ||
                    credits > s.creditsValues[creditsCurrentValues[1]]) {
                        show = false;
                }
            }
            if (show) {
                var rating = 0.0;
                var rating_item = $(this).find(s.courseRatingsSelector);
                if (rating_item.length > 0) {
                    rating = parseFloat( rating_item.text() );
                }
                if ((ratingsCurrentValues[0] > 0 && rating < s.ratingsValues[ratingsCurrentValues[0]]) ||
                    (ratingsCurrentValues[1] > 0 && rating > s.ratingsValues[ratingsCurrentValues[1]])) {
                        show = false;
                }
                if (ratingsCurrentValues[1] == 0 && rating > 0) {
                    show = false;
                }
            }
            if (show) {
                course_name = $(this).find(s.courseNameSelector).find('a').text();
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

        // $("img.course-image").lazyload({
        //     event : "click"
        // });
    };

    /*************************************
        Category Checkbox All-vs-normal
    **************************************/
    me.categoryCheckboxHandle = function() {
        var $this = $(this);
        var $parent = $this.parents(s.categoryCheckboxWrapperSelector);
        var $cb_all = $parent.find(s.checkboxAllSelector);

        if ($this.hasClass('cb-all')) {
            $parent.find(s.checkboxNormalSelector).prop('checked', false);
            $cb_all.prop('checked', 'true');
        }
        var $checked = $parent.find(s.categoryCheckboxSelector).filter( ':checked' );
        if ($checked.length > 0) {
            if ($checked.not(s.checkboxAllSelector).length > 0) {
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
                s.categoriesSearchWrapper.html(result.html);
                $(s.categoryCheckboxSelector).change(ExplorePage.categoryCheckboxHandle);
                ExplorePage.indexCourses();
            },
            error: function() {
            }
        });

    };

    /*************************************
        Sliders handle code!
    **************************************/
    me.sliderStop = function(event, ui) {
        ExplorePage.indexCourses();
    };

    /*************************************
        Credit slider handle code!
    **************************************/
    me.creditsSliderChange = function(event, ui) {
        $("#credits_handle_0").val( s.creditsValues[ ui.values[0] ] )
        $("#credits_handle_1").val( s.creditsValues[ ui.values[1] ] )
    };

    /*************************************
        Ratings slider handle code!
    **************************************/
    me.ratingsSliderChange = function(event, ui) {
        $("#ratings_handle_0").val( s.ratingsValues[ ui.values[0] ] )
        $("#ratings_handle_1").val( s.ratingsValues[ ui.values[1] ] )
    };

    return me;
}());

ExplorePage.init();