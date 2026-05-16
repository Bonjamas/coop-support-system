// Side-specifik JS for "Opret ticket" (kun admin/support).
// Den fælles setupSearch() ligger i common.js.

setupSearch("requestedSearch", "requestedResults", "requested_oid");
setupSearch("assignedSearch", "assignedResults", "assigned_oid");

// Stop submit hvis admin/support ikke har valgt en rigtig person under "Anmodet af".
document.getElementById("createForm").addEventListener("submit", function (e) {
    if (!document.getElementById("requested_oid").value) {
        alert('Vælg en person under "Anmodet af"');
        e.preventDefault();
    }
});
