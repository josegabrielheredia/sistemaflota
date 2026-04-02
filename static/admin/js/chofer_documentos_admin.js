(function () {
  function isYes(value) {
    return String(value || "").toLowerCase() === "true";
  }

  function updateDateField(selectId, dateId) {
    const selectField = document.getElementById(selectId);
    const dateField = document.getElementById(dateId);
    if (!selectField || !dateField) return;

    const enabled = isYes(selectField.value);
    dateField.disabled = !enabled;
    dateField.required = enabled;

    if (!enabled) {
      dateField.value = "";
    }
  }

  function bindToggle(selectId, dateId) {
    const selectField = document.getElementById(selectId);
    if (!selectField) return;
    const run = function () {
      updateDateField(selectId, dateId);
    };
    selectField.addEventListener("change", run);
    run();
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindToggle("id_rntt", "id_vencimiento_carnet_rntt");
    bindToggle("id_seguro_ley", "id_vencimiento_seguro_ley");
  });
})();
