document.addEventListener("DOMContentLoaded", () => {
    flatpickr("#data", {
        dateFormat: "Y-m-d",
        minDate: "today",
        defaultDate: document.getElementById("data").value,
        onChange: function(selectedDates, dateStr) {
            window.location.href = "/?data=" + dateStr;
        }
    });

    const form = document.querySelector(".form");
    if (form) {
        form.style.opacity = "0";
        form.style.transition = "opacity 0.5s";
        setTimeout(() => {
            form.style.opacity = "1";
        }, 100);
    }

    const agendaItems = document.querySelectorAll(".agenda-item");
    agendaItems.forEach((item, index) => {
        item.style.opacity = "0";
        item.style.transform = "translateY(20px)";
        setTimeout(() => {
            item.style.transition = "opacity 0.5s, transform 0.5s";
            item.style.opacity = "1";
            item.style.transform = "translateY(0)";
        }, index * 100);
    });
});