// El formulario mantiene el flujo HTML nativo para descargar el PDF generado.
document.addEventListener('DOMContentLoaded', () => {
    // Se obtienen elementos existentes sin modificar la validacion del navegador.
    const form = document.getElementById('invoice-form');
    const boton = document.getElementById('generate-btn');
    const etiqueta = document.getElementById('button-label');
    // Al enviar se informa al usuario que la solicitud esta siendo procesada.
    if (form && boton && etiqueta) {
        form.addEventListener('submit', () => {
            etiqueta.textContent = 'Preparando factura PDF...';
            // Se mantiene el boton habilitado porque la descarga no provoca nueva pagina.
            // No se simula un progreso ni se promete que el servidor haya respondido.
        });
    }
});
