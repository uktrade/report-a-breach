document.addEventListener("DOMContentLoaded", function () {
    const searchBox =
        document.getElementById('id_which_breach_report-search_bar');
    checkboxContainer = document.getElementById('govuk-checkboxes');
    searchBox.addEventListener("keyup",
        function () {
            const value = this.value.toLowerCase();
            const items = document.querySelectorAll('label[class="govuk-label govuk-checkboxes__label"]');
            items.forEach(function (item) {
                const text = item.textContent || item.innerText;
                item.parentNode.style.display = text.toLowerCase().includes(value) ? "block" : "none";
            });
            if (value.length > 0) {
                document.getElementsByClassName('govuk-checkboxes__divider')[0].style.display = "none";
            }
        });
});
