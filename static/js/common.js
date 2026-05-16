// Fælles JS-hjælpere brugt af flere sider. Loades fra base.html.
//
// Indeholder:
//   1) setupSearch()  - bruger-autocomplete til "Anmodet af" / "Tildelt til"
//   2) Auto-init af #ticket-table: sortering + søgefelt-filter
//   3) Auto-init af .delete-ticket-form: confirm-dialog før submit


// ============================================================
// 1) Bruger-søgning (Entra ID-lookup via /api/users)
// ============================================================
// Bruges af "Opret ticket" og ticket-detalje-siden af admin/support.
// inputId   = synligt felt brugeren skriver i
// resultsId = div hvor søgeresultaterne vises
// oidId     = skjult input der gemmer brugerens OID
window.setupSearch = function (inputId, resultsId, oidId) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);

    if (!input || !results) return;

    // Hver gang brugeren skriver: spørg backend efter matchende brugere.
    input.addEventListener("input", async () => {
        const q = input.value;
        if (q.length < 2) { results.classList.add("hidden"); return; }

        try {
            const res = await fetch(`/api/users?q=${encodeURIComponent(q)}`);
            const users = await res.json();

            results.innerHTML = "";
            results.classList.remove("hidden");

            if (users.length === 0) {
                const empty = document.createElement("div");
                empty.className = "p-2 text-xs text-gray-400";
                empty.innerText = "Ingen resultater";
                results.appendChild(empty);
            } else {
                // Ét klikbart resultat pr. bruger.
                users.forEach(u => {
                    const div = document.createElement("div");
                    div.className = "p-2 hover:bg-gray-100 cursor-pointer";
                    div.innerText = u.name;
                    div.onclick = () => {
                        document.getElementById(oidId).value = u.oid;
                        input.value = u.name;
                        results.classList.add("hidden");
                    };
                    results.appendChild(div);
                });
            }
        } catch {
            results.classList.add("hidden");
        }
    });

    // Hvis brugeren retter teksten manuelt: nulstil OID,
    // så vi ikke gemmer et navn der ikke matcher en bruger.
    input.addEventListener("change", () => {
        const hidden = document.getElementById(oidId);
        if (hidden) hidden.value = "";
    });

    // Klik udenfor: luk resultat-listen.
    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.classList.add("hidden");
        }
    });
};


// ============================================================
// 2) Ticket-tabel: sortering + søgning
// ============================================================
// Aktiveres automatisk hvis siden indeholder en #ticket-table.
// Hver <th> skal have et data-type ("number" / "string" / "rank"),
// og hver <td> skal have data-value som sorteringen bruger.

const TABLE_SORT_KEY = "sort_tickets";

function initTicketTable(table) {
    const tbody = table.querySelector("tbody");
    const headers = table.querySelectorAll("th");

    // Hent gemt sortering, eller default: kolonne 8 (Opdateret), faldende.
    let state;
    const saved = sessionStorage.getItem(TABLE_SORT_KEY);
    state = saved ? JSON.parse(saved) : { col: 8, asc: false };

    function updateIcons() {
        headers.forEach((th, i) => {
            const icon = th.querySelector(".sort-icon");
            if (!icon) return;
            icon.textContent = (i === state.col) ? (state.asc ? "↑" : "↓") : "";
        });
    }

    function sortRows() {
        if (state.col < 0 || state.col >= headers.length) return;
        const type = headers[state.col].dataset.type;
        const rows = Array.from(tbody.querySelectorAll("tr"));

        rows.sort((a, b) => {
            const av = a.cells[state.col]?.dataset.value ?? "";
            const bv = b.cells[state.col]?.dataset.value ?? "";
            const cmp = (type === "number" || type === "rank")
                ? Number(av) - Number(bv)
                : av.localeCompare(bv, "da");
            return state.asc ? cmp : -cmp;
        });

        rows.forEach(r => tbody.appendChild(r));
    }

    // Eksponer handleSort globalt så onclick="handleSort(this)" i HTML virker.
    window.handleSort = function (th) {
        const idx = th.cellIndex;
        if (state.col === idx) {
            state.asc = !state.asc;
        } else {
            state.col = idx;
            state.asc = true;
        }
        sessionStorage.setItem(TABLE_SORT_KEY, JSON.stringify(state));
        updateIcons();
        sortRows();
    };

    updateIcons();
    sortRows();
}

function initTableSearch() {
    const search = document.getElementById("search");
    const tbody = document.getElementById("ticket-tbody");
    if (!search || !tbody) return;

    // Skjul rækker der ikke indeholder søgeteksten.
    search.addEventListener("input", function () {
        const q = this.value.toLowerCase();
        tbody.querySelectorAll("tr").forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? "" : "none";
        });
    });
}


// ============================================================
// 3) Slet-confirm for forms med klasse .delete-ticket-form
// ============================================================
// Form'en skal selv levere bekræftelses-teksten i data-confirm-message.
function initDeleteConfirms() {
    document.querySelectorAll(".delete-ticket-form").forEach(form => {
        form.addEventListener("submit", e => {
            if (!confirm(form.dataset.confirmMessage)) {
                e.preventDefault();
            }
        });
    });
}


// ============================================================
// Start alt op når DOM'en er klar
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("ticket-table");
    if (table) {
        initTicketTable(table);
        initTableSearch();
    }
    initDeleteConfirms();
});
