document.addEventListener("DOMContentLoaded", function() {
    // hide the optional question by default
    $('.optional_question').hide()

    $(document).on('mouseover', '.star-rating__label', function(){
        // on hover, change the color of the stars and change the text to reflect the choice
        let rating_name = $(this).data('rating-name')
        let rating_value = $(this).data('rating-value')
        $('#js_selected_rating').html(rating_name)

        // filling up the previous starts
        $(this).prevAll('.star-rating__label').addClass('star-rating__selected')
        $(this).addClass('star-rating__selected')

        // emptying the next stars
        $(this).nextAll('.star-rating__label').removeClass('star-rating__selected')
    })

    $(document).on("click", ".star-rating__label", function(){
        // on click of the star, set the value of the rating and hide the optional question if the rating is 4 or less
        let rating_value = $(this).data('rating-value')
        let rating_name = $(this).data('rating-name')
        $('#chosen_rating').val(rating_value)
        $('#js_selected_rating').html(rating_name).data('frozen', true)

        if (rating_value <= 4) {
            $('.optional_question').show()
        } else {
            $('.optional_question').hide()
        }
    })

    // on page load, show/hide the optional question based on the rating which may have already been
    // selected by the user on a previous screen
    $('.star-rating__selected').last().trigger('click')
})
