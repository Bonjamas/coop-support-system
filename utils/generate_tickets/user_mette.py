USER = {
    "key": "mette",
    "oid": "24ac334a-e2c2-4aa4-b40c-6de5f143497f",
    "name": "Mette Hansen",
    "role": "user",
}

TICKETS = [
    {
        "title": "Kan ikke tilgå vagtplan",
        "description": "Får fejl 403 når jeg forsøger at åbne vagtplanen. Har prøvet i Chrome og Edge.",
        "priority": "low",
        "type": "support",
        "contact": "mette.hansen@coop.dk",
        "events": [
            {"event_type": "assign", "actor": "support1", "assignee": "support1"},
            {"event_type": "comment", "actor": "mette", "text": "Jeg har ikke ændret noget — det virkede fint i går."},
            {"event_type": "note", "actor": "support1", "text": "Din bruger mangler rettighed til vagtplan-modulet. Tilføjer nu."},
        ],
    },
]
