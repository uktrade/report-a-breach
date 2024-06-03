document.addEventListener("DOMContentLoaded", function() {
    // hide the optional question by default
    $('.optional_question').hide()
    $('#div_id_did_you_experience_any_issues').hide()

    $(document).on("change", "input[name='rating']", function(){
        // on change of a rating
        let rating_value = $(this).val()
        if (rating_value <= 4) {
            $('#div_id_did_you_experience_any_issues').show()
            $('.optional_question').show()
        } else {
            $('#div_id_did_you_experience_any_issues').hide()
            $('.optional_question').hide()
        }
    })

    // on page load, show/hide the optional question based on the rating which may have already been
    // selected by the user on a previous screen
    $("input[name='rating']:checked").trigger('change')
})
