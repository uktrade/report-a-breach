document.addEventListener("DOMContentLoaded", function (event) {
    $('input[name$="which_sanctions_regime"][value="Unknown Regime"]').on('change', function () {
        if ($(this).is(':checked')) {
            // clear the other regime inputs
            $('.govuk-checkboxes__divider').prevAll().find('input[name$="which_sanctions_regime"]').prop('checked', false);
        }
    });

    $('.govuk-checkboxes__divider').prevAll().find('input[name$="which_sanctions_regime"]').on('change', function () {
        if ($(this).is(':checked')) {
            // clear the unknown regime input
            $('input[name$="which_sanctions_regime"][value="Unknown Regime"]').prop('checked', false);
        }
    });

});
