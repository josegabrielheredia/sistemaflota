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

  function updateConducesByChofer(choferId) {
    const conducesField = document.getElementById("id_conduces");
    if (!conducesField) return;

    const previousSelected = new Set(
      Array.from(conducesField.selectedOptions || []).map((option) => String(option.value))
    );
    conducesField.innerHTML = "";

    if (!choferId) {
      return;
    }

    const template = window.__pagoConducesUrlTemplate || "";
    const endpoint = template.replace("/0/", "/" + choferId + "/");
    fetch(endpoint, { credentials: "same-origin" })
      .then(function (response) {
        return response.ok ? response.json() : { conduces: [] };
      })
      .then(function (data) {
        (data.conduces || []).forEach(function (item) {
          const option = document.createElement("option");
          option.value = String(item.id);
          option.text = item.texto;
          option.selected = previousSelected.has(String(item.id));
          conducesField.appendChild(option);
        });
      })
      .catch(function () {
        conducesField.innerHTML = "";
      });
  }

  function addConduceButton() {
    const choferField = document.getElementById("id_chofer");
    const conducesField = document.getElementById("id_conduces");
    const addUrl = window.__conduceAddUrl || "";
    if (!choferField || !conducesField || !addUrl) return;
    if (document.getElementById("btn-add-conduce-inline")) return;

    const wrapper = document.createElement("div");
    wrapper.style.marginTop = "8px";
    wrapper.style.display = "flex";
    wrapper.style.gap = "8px";
    wrapper.style.alignItems = "center";

    const button = document.createElement("button");
    button.type = "button";
    button.id = "btn-add-conduce-inline";
    button.className = "button";
    button.textContent = "Agregar conduce ahora";

    const help = document.createElement("small");
    help.style.color = "#64748b";
    help.textContent = "Se abrira una ventana y al guardar se actualizara la lista.";

    wrapper.appendChild(button);
    wrapper.appendChild(help);
    conducesField.insertAdjacentElement("afterend", wrapper);

    button.addEventListener("click", function () {
      const choferId = choferField.value;
      if (!choferId) {
        window.alert("Primero selecciona el chofer para crear el conduce.");
        choferField.focus();
        return;
      }

      const popupUrl =
        addUrl +
        "?_popup=1&chofer=" +
        encodeURIComponent(choferId) +
        "&_to_field=id";

      const popup = window.open(
        popupUrl,
        "id_conduces",
        "height=700,width=1050,resizable=yes,scrollbars=yes"
      );

      if (!popup) {
        window.alert("No se pudo abrir la ventana emergente. Revisa el bloqueador de popups.");
        return;
      }

      const refreshWhenClosed = window.setInterval(function () {
        if (popup.closed) {
          window.clearInterval(refreshWhenClosed);
          updateConducesByChofer(choferField.value);
        }
      }, 500);
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
      updateConducesByChofer(choferField.value);
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
    updateConducesByChofer(choferField.value);
    addConduceButton();
  });
})();
