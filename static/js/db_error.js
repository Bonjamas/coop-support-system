// Tæller ned fra 5 sek. og henter forsiden igen automatisk,
// så brugeren ikke selv skal trykke "opdater" når databasen er nede igen.
let seconds = 5;
const text = document.getElementById("refresh-text");

const interval = setInterval(() => {
    seconds--;
    text.innerText = `Siden opdateres automatisk om ${seconds} sekunder...`;
    if (seconds <= 0) {
        clearInterval(interval);
        window.location.href = "/";
    }
}, 1000);
