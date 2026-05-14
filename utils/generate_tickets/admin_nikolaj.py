USER = {
    "key": "admin",
    "oid": "a59ecfe8-c8b2-4f6c-a760-980a914c7177",
    "name": "Nikolaj Admin",
    "role": "admin",
}

TICKETS = [
    {
        "title": "Kritisk fejl i POS-integrationslag",
        "description": "Integrationen mellem kassesystemet og regnskabsplatformen sender dubletter. Berører alle butikker.",
        "priority": "high",
        "type": "nedbrud",
        "contact": "nikolaj.admin@coop.dk",
        "events": [
            {"event_type": "assign", "udfører": "admin", "assignee": "admin"},
            {"event_type": "note", "udfører": "admin", "text": "Fejlen opstod efter gårsdagens deploy af integrations-service v2.3.1. Ruller tilbage til v2.3.0."},
            {"event_type": "note", "udfører": "admin", "text": "Tilbagerulning gennemført. Overvåger for nye dubletter de næste 2 timer."},
        ],
    },
    {
        "title": "Serverrum i Greve — unormal temperatur",
        "description": "Temperaturalarm fra serverrum i Greve. Klimaanlæg mistænkes. Skal følges op med facility.",
        "priority": "high",
        "type": "nedbrud",
        "contact": "29 83 17 44",
        "events": [
            {"event_type": "assign", "udfører": "admin", "assignee": "admin"},
            {"event_type": "note", "udfører": "admin", "text": "Temperatur er 28°C — grænsen er 25°C. Facility er kontaktet. Afventer svar."},
            {"event_type": "comment", "udfører": "greve", "text": "Vi har åbnet serverrumsdøren midlertidigt for at ventilere."},
            {"event_type": "note", "udfører": "admin", "text": "Facility bekræfter at klimaanlægget er defekt. Tekniker ankommer i morgen. Overvåger temperatur."},
        ],
    },
    {
        "title": "Opdatering af POS-software til v4.12",
        "description": "Planlagt udrulning af ny POS-version til alle butikker. Koordineres med butikscheferne.",
        "priority": "medium",
        "type": "funktionalitet",
        "contact": "nikolaj.admin@coop.dk",
        "events": [
            {"event_type": "assign", "udfører": "admin", "assignee": "admin"},
            {"event_type": "note", "udfører": "admin", "text": "Udrulning planlagt til søndag nat kl. 02:00. Butikkerne er varslet."},
            {"event_type": "note", "udfører": "admin", "text": "Testinstallation på Karlslunde gennemført uden fejl. Fortsætter med de øvrige."},
        ],
    },
    {
        "title": "Massiv loginproblematik efter AD-synkronisering",
        "description": "Efter synkronisering med Active Directory kunne 12 medarbejdere på tværs af butikker ikke logge ind.",
        "priority": "high",
        "type": "nedbrud",
        "contact": "nikolaj.admin@coop.dk",
        "events": [
            {"event_type": "assign", "udfører": "admin", "assignee": "admin"},
            {"event_type": "note", "udfører": "admin", "text": "AD-synkroniseringen overskrev lokale brugerkonti med forkerte attributter. Rullet tilbage."},
            {"event_type": "note", "udfører": "admin", "text": "Alle 12 konti er gendannet og testet. Identificerer årsagen til at synkroniseringen fejlede."},
            {"event_type": "resolve", "udfører": "admin"},
        ],
    },
    {
        "title": "Certifikat udløbet på betalingsgateway",
        "description": "SSL-certifikat på betalingsgateway udløb og forårsagede fejl på alle Dankort-transaktioner.",
        "priority": "high",
        "type": "nedbrud",
        "contact": "nikolaj.admin@coop.dk",
        "events": [
            {"event_type": "assign", "udfører": "admin", "assignee": "admin"},
            {"event_type": "note", "udfører": "admin", "text": "Nyt certifikat udstedt og installeret. Betalinger virker igen. Opretter reminder 30 dage før næste udløb."},
            {"event_type": "resolve", "udfører": "admin"},
        ],
    },
]
