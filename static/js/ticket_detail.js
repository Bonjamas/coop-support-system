// Side-specifik JS for ticket-detalje-siden (kun admin/support).
// Den fælles setupSearch() ligger i common.js.

setupSearch("requestedSearch", "requestedResults", "requested_oid");
setupSearch("assignedSearch", "assignedResults", "assigned_oid");

// "Løs"-knappen: sætter state-dropdown til "resolved" lige inden formularen sendes.
function setResolved() {
    const stateSelect = document.querySelector('select[name="state"]');
    if (stateSelect) stateSelect.value = "resolved";
}
