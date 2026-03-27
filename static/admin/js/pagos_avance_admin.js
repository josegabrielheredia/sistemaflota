(function () {
  function formatCurrency(value) {
    const amount = Number(value || 0);
    return amount.toFixed(2);
  }

  function updateSaldo(choferId) {
    const saldoField = document.getElementById("id_saldo_avance_pendiente");
    const liquidarField = document.getElementById("id_liquidar_avances_pendientes");
    if (!saldoField || !liquidarField) return;

    if (!choferId) {
      saldoField.value = formatCurrency(0);
      liquidarField.checked = false;
      liquidarField.disabled = true;
      return;
    }

    const template = window.__pagoSaldoUrlTemplate || "";
    const endpoint = template.replace("/0/", "/" + choferId + "/");
    fetch(endpoint, { credentials: "same-origin" })
      .then(function (response) {
        return response.ok ? response.json() : { saldo_pendiente: "0.00", tiene_pendiente: false };
      })
      .then(function (data) {
        saldoField.value = formatCurrency(data.saldo_pendiente);
        liquidarField.disabled = !data.tiene_pendiente;
        if (!data.tiene_pendiente) {
          liquidarField.checked = false;
        }
      })
      .catch(function () {
        saldoField.value = formatCurrency(0);
        liquidarField.checked = false;
        liquidarField.disabled = true;
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const choferField = document.getElementById("id_chofer");
    if (!choferField) return;

    choferField.addEventListener("change", function () {
      updateSaldo(choferField.value);
    });

    updateSaldo(choferField.value);
  });
})();
