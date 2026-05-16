// "Slet alt"-knappen: spørg lige brugeren om de er sikre,
// før formularen sendes og alle tickets bliver slettet permanent.
document.getElementById("deleteAllForm").addEventListener("submit", function (e) {
    if (!confirm("Er du SIKKER? Alle tickets og kommentarer slettes.")) {
        e.preventDefault();
    }
});
