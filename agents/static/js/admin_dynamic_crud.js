document.addEventListener('DOMContentLoaded', function() {
    function handleDjangoRelatedButtons(selectElement) {
        const wrapper = selectElement.closest('.related-widget-wrapper');
        if (!wrapper) return;

        const id = selectElement.value;
        const btnEdit = wrapper.querySelector('.change-related');
        const btnShow = wrapper.querySelector('.view-related');

        // Gestion de la modification (✏️)
        if (btnEdit) {
            if (id) {
                const template = btnEdit.getAttribute('data-href-template');
                if (template) {
                    btnEdit.href = template.replace('__fk__', id);
                    btnEdit.style.opacity = "1";
                    btnEdit.style.pointerEvents = "auto";
                }
            } else {
                btnEdit.removeAttribute('href');
                btnEdit.style.opacity = "0.3";
                btnEdit.style.pointerEvents = "none";
            }
        }

        // Gestion de la visualisation (👁️)
        if (btnShow) {
            if (id) {
                const template = btnShow.getAttribute('data-href-template');
                if (template) {
                    btnShow.href = template.replace('__fk__', id);
                    btnShow.style.opacity = "1";
                    btnShow.style.pointerEvents = "auto";
                }
            } else {
                btnShow.removeAttribute('href');
                btnShow.style.opacity = "0.3";
                btnShow.style.pointerEvents = "none";
            }
        }
    }

    document.addEventListener('change', function(event) {
        if (event.target && event.target.tagName === 'SELECT') {
            handleDjangoRelatedButtons(event.target);
        }
    });

    setTimeout(() => {
        document.querySelectorAll('.related-widget-wrapper select').forEach(select => {
            handleDjangoRelatedButtons(select);
        });
    }, 600);
});