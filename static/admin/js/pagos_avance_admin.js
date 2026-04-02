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

  function updateChequeFieldState() {
    const metodoField = document.getElementById("id_metodo");
    const numeroChequeField = document.getElementById("id_numero_cheque");
    if (!metodoField || !numeroChequeField) return;

    const esCheque = metodoField.value === "cheque";
    numeroChequeField.disabled = !esCheque;
    if (!esCheque) {
      numeroChequeField.value = "";
    }
  }

  function updateMontoNeto() {
    const montoField = document.getElementById("id_monto");
    const descontarField = document.getElementById("id_descontar_suministro_combustible");
    const cobroField = document.getElementById("id_monto_a_cobrar_combustible");
    const netoField = document.getElementById("id_monto_neto_a_pagar");
    if (!montoField || !descontarField || !cobroField || !netoField) return;

    const monto = parseAmount(montoField.value);
    const cobro = parseAmount(cobroField.value);
    const descuento = descontarField.checked
      ? Math.min(monto, currentSaldoPendiente, Math.max(cobro, 0))
      : 0;
    const neto = Math.max(monto - descuento, 0);
    netoField.value = formatCurrency(neto);
  }

  function updateSaldo(choferId) {
    const saldoField = document.getElementById("id_saldo_combustible_pendiente");
    const descontarField = document.getElementById("id_descontar_suministro_combustible");
    const cobroField = document.getElementById("id_monto_a_cobrar_combustible");
    const montoField = document.getElementById("id_monto");
    if (!saldoField || !descontarField || !cobroField || !montoField) return;

    if (!choferId) {
      saldoField.value = formatCurrency(0);
      currentSaldoPendiente = 0;
      descontarField.checked = false;
      descontarField.disabled = true;
      cobroField.value = formatCurrency(0);
      cobroField.disabled = true;
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
        cobroField.disabled = !data.tiene_pendiente;
        const montoActual = parseAmount(montoField.value);
        cobroField.value = formatCurrency(Math.min(currentSaldoPendiente, montoActual));
        if (!data.tiene_pendiente) {
          descontarField.checked = false;
          cobroField.value = formatCurrency(0);
        }
        updateMontoNeto();
      })
      .catch(function () {
        saldoField.value = formatCurrency(0);
        currentSaldoPendiente = 0;
        descontarField.checked = false;
        descontarField.disabled = true;
        cobroField.value = formatCurrency(0);
        cobroField.disabled = true;
        updateMontoNeto();
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const choferField = document.getElementById("id_chofer");
    const montoField = document.getElementById("id_monto");
    const descontarField = document.getElementById("id_descontar_suministro_combustible");
    const cobroField = document.getElementById("id_monto_a_cobrar_combustible");
    const metodoField = document.getElementById("id_metodo");
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

    if (cobroField) {
      cobroField.addEventListener("input", updateMontoNeto);
      cobroField.addEventListener("change", updateMontoNeto);
    }

    if (metodoField) {
      metodoField.addEventListener("change", updateChequeFieldState);
      updateChequeFieldState();
    }

    updateSaldo(choferField.value);
  });
})();
