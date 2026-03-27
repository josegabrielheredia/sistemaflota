(function () {
  var currentSaldoPendiente = 0;

  function formatCurrency(value) {
    const amount = Number(value || 0);
    return amount.toFixed(2);
  }

  function parseAmount(value) {
    if (value === null || value === undefined || value === "") return 0;
    return Number(String(value).replace(/,/g, "")) || 0;
  }

  function updateMontoNeto() {
    const montoField = document.getElementById("id_monto");
    const descontarField = document.getElementById("id_descontar_avance_pendiente");
    const netoField = document.getElementById("id_monto_neto_a_pagar");
    if (!montoField || !descontarField || !netoField) return;

    const monto = parseAmount(montoField.value);
    const descuento = descontarField.checked ? Math.min(monto, currentSaldoPendiente) : 0;
    const neto = Math.max(monto - descuento, 0);
    netoField.value = formatCurrency(neto);
  }

  function updateSaldo(choferId) {
    const saldoField = document.getElementById("id_saldo_avance_pendiente");
    const descontarField = document.getElementById("id_descontar_avance_pendiente");
    if (!saldoField || !descontarField) return;

    if (!choferId) {
      saldoField.value = formatCurrency(0);
      currentSaldoPendiente = 0;
      descontarField.checked = false;
      descontarField.disabled = true;
      updateMontoNeto();
      return;
    }

    const template = window.__pagoSaldoUrlTemplate || "";
    const endpoint = template.replace("/0/", "/" + choferId + "/");
    fetch(endpoint, { credentials: "same-origin" })
      .then(function (response) {
        return response.ok ? response.json() : { saldo_pendiente: "0.00", tiene_pendiente: false };
      })
      .then(function (data) {
        currentSaldoPendiente = parseAmount(data.saldo_pendiente);
        saldoField.value = formatCurrency(currentSaldoPendiente);
        descontarField.disabled = !data.tiene_pendiente;
        if (!data.tiene_pendiente) {
          descontarField.checked = false;
        }
        updateMontoNeto();
      })
      .catch(function () {
        saldoField.value = formatCurrency(0);
        currentSaldoPendiente = 0;
        descontarField.checked = false;
        descontarField.disabled = true;
        updateMontoNeto();
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const choferField = document.getElementById("id_chofer");
    const montoField = document.getElementById("id_monto");
    const descontarField = document.getElementById("id_descontar_avance_pendiente");
    if (!choferField) return;

    choferField.addEventListener("change", function () {
      updateSaldo(choferField.value);
    });

    if (montoField) {
      montoField.addEventListener("input", updateMontoNeto);
      montoField.addEventListener("change", updateMontoNeto);
    }

    if (descontarField) {
      descontarField.addEventListener("change", updateMontoNeto);
    }

    updateSaldo(choferField.value);
  });
})();
