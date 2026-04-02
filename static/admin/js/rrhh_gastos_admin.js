(function () {
  function toggleNumeroComprobante() {
    const conComprobanteField = document.getElementById("id_con_comprobante");
    const numeroComprobanteField = document.getElementById("id_numero_comprobante");
    if (!conComprobanteField || !numeroComprobanteField) return;

    const activo = !!conComprobanteField.checked;
    numeroComprobanteField.disabled = !activo;
    numeroComprobanteField.required = activo;
    if (!activo) {
      numeroComprobanteField.value = "";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const conComprobanteField = document.getElementById("id_con_comprobante");
    if (!conComprobanteField) return;
    conComprobanteField.addEventListener("change", toggleNumeroComprobante);
    toggleNumeroComprobante();
  });
})();
