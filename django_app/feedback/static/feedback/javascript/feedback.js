document.addEventListener("DOMContentLoaded", function() {
    // hide the optional question by default
    $('.optional_question').hide()

    $(document).on("change", "input[name='rating']", function(){
        // on change of a rating
        let rating_value = $(this).val()
        if (rating_value <= 4) {
            $('.optional_question').show()
        } else {
            $('.optional_question').hide()
        }
    })

    // on page load, show/hide the optional question based on the rating which may have already been
    // selected by the user on a previous screen
    $("input[name='rating']:checked").trigger('change')
})
