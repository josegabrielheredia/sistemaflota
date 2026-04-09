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

  function updateChasis() {
    const conChasisField = document.getElementById("id_con_chasis");
    const chasisField = document.getElementById("id_chasis");
    if (!conChasisField || !chasisField) return;

    const enabled = conChasisField.checked;
    chasisField.disabled = !enabled;
    chasisField.required = enabled;
    if (!enabled) {
      chasisField.value = "";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const formaField = document.getElementById("id_forma_pago");
    const conChasisField = document.getElementById("id_con_chasis");

    if (formaField) {
      formaField.addEventListener("change", updateReferencia);
      updateReferencia();
    }

    if (conChasisField) {
      conChasisField.addEventListener("change", updateChasis);
      updateChasis();
    }
  });
})();
