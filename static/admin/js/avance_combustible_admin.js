(function () {
  function parseAmount(value) {
    if (value === null || value === undefined || value === "") return 0;
    return Number(String(value).replace(/,/g, "")) || 0;
  }

  function formatAmount(value) {
    const amount = Number(value || 0);
    return amount.toFixed(2);
  }

  function updateMontoSuministro() {
    const galonesField = document.getElementById("id_galones");
    const precioField = document.getElementById("id_precio_por_galon");
    const montoField = document.getElementById("id_monto");
    if (!galonesField || !precioField || !montoField) return;

    const galones = parseAmount(galonesField.value);
    const precio = parseAmount(precioField.value);
    const monto = Math.max(galones * precio, 0);
    montoField.value = formatAmount(monto);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const galonesField = document.getElementById("id_galones");
    const precioField = document.getElementById("id_precio_por_galon");
    if (!galonesField || !precioField) return;

    galonesField.addEventListener("input", updateMontoSuministro);
    galonesField.addEventListener("change", updateMontoSuministro);
    precioField.addEventListener("input", updateMontoSuministro);
    precioField.addEventListener("change", updateMontoSuministro);

    updateMontoSuministro();
  });
})();
