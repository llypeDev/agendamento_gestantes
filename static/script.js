document.addEventListener("DOMContentLoaded", () => {
    // Inicialização do Flatpickr para inputs de data
    const initializeFlatpickr = () => {
        // Para index.html
        const indexDataInput = document.getElementById("data");
        if (indexDataInput) {
            flatpickr(indexDataInput, {
                dateFormat: "Y-m-d",
                minDate: "today",
                defaultDate: indexDataInput.value,
                onChange: function(selectedDates, dateStr) {
                    window.location.href = "/?data=" + dateStr;
                }
            });
        }

        // Para gestante_edit.html (inputs dinâmicos com IDs como data_1, data_2, etc.)
        const editDataInputs = document.querySelectorAll("input[id^='data_']");
        editDataInputs.forEach(input => {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                minDate: "today",
                defaultDate: input.value
            });
        });
    };

    // Verifica se o Flatpickr está carregado antes de inicializar
    if (typeof flatpickr === "undefined") {
        console.error("Flatpickr não foi carregado. Verifique o CDN.");
    } else {
        initializeFlatpickr();
    }

    // Animação do formulário (index, login, gestante_login, gestante_edit)
    const forms = document.querySelectorAll(".form-grid");
    forms.forEach(form => {
        form.style.opacity = "0";
        form.style.transform = "translateY(20px)";
        setTimeout(() => {
            form.style.transition = "opacity 0.5s, transform 0.5s";
            form.style.opacity = "1";
            form.style.transform = "translateY(0)";
        }, 100);
    });

    // Animação dos cards da agenda (index)
    const agendaCards = document.querySelectorAll(".agenda-card");
    agendaCards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "opacity 0.5s, transform 0.5s";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 50);
    });

    // Animação da tabela admin
    const adminRows = document.querySelectorAll(".admin-table tr");
    adminRows.forEach((row, index) => {
        row.style.opacity = "0";
        row.style.transform = "translateY(20px)";
        setTimeout(() => {
            row.style.transition = "opacity 0.5s, transform 0.5s";
            row.style.opacity = "1";
            row.style.transform = "translateY(0)";
        }, index * 50);
    });
});