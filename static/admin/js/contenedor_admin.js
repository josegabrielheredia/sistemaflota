(function () {
  function isTransferOrCheque(value) {
    const v = String(value || "").toLowerCase();
    return v === "transferencia" || v === "cheque";
  }

  function updateReferencia() {
    const formaField = document.getElementById("id_forma_pago");
    const refField = document.getElementById("id_numero_referencia_pago");
    if (!formaField || !refField) return;

    const enabled = isTransferOrCheque(formaField.value);
    refField.disabled = !enabled;
    refField.required = enabled;
    if (!enabled) {
      refField.value = "";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const formaField = document.getElementById("id_forma_pago");
    if (!formaField) return;
    formaField.addEventListener("change", updateReferencia);
    updateReferencia();
  });
})();
