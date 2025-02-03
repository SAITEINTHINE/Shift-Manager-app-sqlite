document.addEventListener("DOMContentLoaded", function () {
    let forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            if (!confirm("Are you sure you want to proceed?")) {
                e.preventDefault();
            }
        });
    });
});