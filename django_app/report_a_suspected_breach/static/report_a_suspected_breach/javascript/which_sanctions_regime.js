document.addEventListener("DOMContentLoaded", function (event) {
    $(document).on('change', 'input[value="Unknown Regime"], input[value="Other Regime"]', function(){
        if ($(this).is(':checked')) {
            // clear the other inputs
            $('input[name$="which_sanctions_regime"]').not($(this)).prop('checked', false);
        }
    })

    $('.govuk-checkboxes__divider').prevAll().find('input[name$="which_sanctions_regime"]').on('change', function () {
        if ($(this).is(':checked')) {
            // clear the unknown regime input
            $('input[name$="which_sanctions_regime"][value="Unknown Regime"]').prop('checked', false);
            $('input[name$="which_sanctions_regime"][value="Other Regime"]').prop('checked', false);
        }
    });

});
