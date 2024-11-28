// Reset form on page reload
$(window).bind("pageshow", function(event) {
    $("#main-content").find("form")[0].reset()

    // hide the optional question by default
    $('.optional_question').hide()

    $(document).on("change", "input[name='rating']", function () {
        // on change of a rating
        let rating_value = $(this).val()
        if (rating_value <= 4) {
            $('.optional_question').show()
        } else {
            $('.optional_question').hide()
        }
    })
});
