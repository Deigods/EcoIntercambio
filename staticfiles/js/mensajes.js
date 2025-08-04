document.addEventListener("DOMContentLoaded", function() {
    const MsgForm = document.getElementById("form_submit");
    const msgContainer = document.getElementById("contenedor_ms");

    if (MsgForm && msgContainer) {  // Asegúrate de que ambos elementos existan
        MsgForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const targetDate = event.target;
            const formData = new FormData(targetDate);

            const xhr = new XMLHttpRequest(); // Ajax Fetch

            const endpoint = MsgForm.getAttribute("action");
            const method = MsgForm.getAttribute("method");
            xhr.open(method, endpoint);

            xhr.responseType = 'json';

            xhr.setRequestHeader("HTTP_X_REQUESTED_WITH", "XMLHttpRequest");
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

            xhr.onload = () => {
                console.log(xhr.status, xhr.response);
            
                if (xhr.status === 201) {
                    const respuestaData = xhr.response;
                    let actualMensajeHtml = msgContainer.innerHTML;
            
                    // Establece que todos los mensajes son tuyos
                    const claseMensaje = 'mis_mensajes';
            
                    // Usa la fecha y hora del mensaje (asegúrate de que la propiedad existe)
                    const fechaHora = respuestaData.fecha_hora || new Date().toLocaleString(); // Fallback a la hora actual si no existe
            
                    // Actualiza el HTML del mensaje
                    actualMensajeHtml += `<div class="div_ms ${claseMensaje}"><small>${respuestaData.username} - ${fechaHora}</small><p>${respuestaData.mensaje}</p></div>`;
                    msgContainer.innerHTML = actualMensajeHtml;
                    MsgForm.reset();
            
                } else if (xhr.status === 400) {
                    console.log(xhr.response);
                    
                } else {
                    alert("Un error ocurrió, por favor intenta más tarde.");
                }
            };
            
                   

            xhr.send(formData);
        });
    } else {
        console.error("El formulario o el contenedor de mensajes no existe.");
    }
});
