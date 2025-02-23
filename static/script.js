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
    const forms = document.querySelectorAll(".grid");
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

    // Notificação para instalar o PWA
    let deferredPrompt;

    window.addEventListener('beforeinstallprompt', (e) => {
        // Impede o prompt padrão do navegador
        e.preventDefault();
        deferredPrompt = e;

        // Mostra um modal personalizado
        const installPrompt = document.createElement('div');
        installPrompt.innerHTML = `
            <div class="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
                    <h2 class="text-lg font-semibold text-gray-800 mb-3">Instale o App!</h2>
                    <p class="text-sm text-gray-600 mb-4">Adicione o Agendamento Gestantes à sua tela inicial para um acesso rápido.</p>
                    <div class="flex gap-2">
                        <button id="installBtn" class="bg-pink-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-pink-700 hover:-translate-y-0.5 transition-all duration-200">Instalar</button>
                        <button id="cancelBtn" class="bg-gray-300 text-gray-800 px-4 py-2 rounded-lg font-medium hover:bg-gray-400 hover:-translate-y-0.5 transition-all duration-200">Cancelar</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(installPrompt);

        // Evento para instalar
        document.getElementById('installBtn').addEventListener('click', () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('Usuário aceitou a instalação');
                    } else {
                        console.log('Usuário recusou a instalação');
                    }
                    deferredPrompt = null;
                });
            }
            document.body.removeChild(installPrompt);
        });

        // Evento para cancelar
        document.getElementById('cancelBtn').addEventListener('click', () => {
            document.body.removeChild(installPrompt);
        });
    });

    // Verifica se o app já está instalado
    window.addEventListener('appinstalled', (event) => {
        console.log('App instalado com sucesso');
    });
});