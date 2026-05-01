// static/js/main.js

// ─────────────────────────────────────────────
// 🚀 CUANDO CARGA LA PÁGINA
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    console.log('Sistema de Encomiendas cargado correctamente 🚚');

    // ─────────────────────────────────────────────
    // 🔔 AUTO-CERRAR MENSAJES (flash messages)
    // ─────────────────────────────────────────────
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function (alert) {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 3000); // 3 segundos
    });


    // ─────────────────────────────────────────────
    // ⚠️ CONFIRMAR ACCIONES (Eliminar / Cambiar estado)
    // ─────────────────────────────────────────────
    const botonesConfirm = document.querySelectorAll('.btn-confirm');

    botonesConfirm.forEach(btn => {
        btn.addEventListener('click', function (e) {
            const mensaje = this.getAttribute('data-confirm') || '¿Estás seguro?';

            if (!confirm(mensaje)) {
                e.preventDefault();
            }
        });
    });


    // ─────────────────────────────────────────────
    // 🔍 FILTRO EN TIEMPO REAL (input búsqueda)
    // ─────────────────────────────────────────────
    const searchInput = document.querySelector('input[name="q"]');

    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            console.log('Buscando:', this.value);
        });
    }


    // ─────────────────────────────────────────────
    // 🎯 RESALTAR FILA AL HACER CLICK
    // ─────────────────────────────────────────────
    const filas = document.querySelectorAll('table tr');

    filas.forEach(fila => {
        fila.addEventListener('click', function () {

            // Quitar selección previa
            filas.forEach(f => f.classList.remove('table-active'));

            // Activar selección actual
            this.classList.add('table-active');
        });
    });


    // ─────────────────────────────────────────────
    // 📦 VALIDACIÓN BÁSICA FORMULARIO
    // ─────────────────────────────────────────────
    const form = document.querySelector('form');

    if (form) {
        form.addEventListener('submit', function (e) {

            const inputs = form.querySelectorAll('input[required], select[required]');

            let valido = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    valido = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!valido) {
                e.preventDefault();
                alert('⚠️ Completa todos los campos obligatorios');
            }
        });
    }

});