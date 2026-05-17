USER = {
    "key": "lars",
    "oid": "b29fe159-e5a3-42fa-9ac2-0a9a3af89d3a",
    "name": "Lars Andersen",
    "role": "user",
}

TICKETS = [
    {
        "title": "Adgangskode er udløbet og kan ikke nulstilles",
        "description": "Systemet siger min adgangskode er udløbet, men nulstillingslinket virker ikke. Kan ikke logge ind.",
        "priority": "low",
        "type": "support",
        "contact": "lars.andersen@coop.dk",
        "events": [
            {"event_type": "assign", "actor": "support2", "assignee": "support2"},
            {"event_type": "comment", "actor": "lars", "text": "Jeg har tjekket spam-mappen — der er ikke noget nulstillingsmail."},
            {"event_type": "note", "actor": "support2", "text": "Nulstillingsmailen ryger i spam pga. manglende SPF-record på vores mailserver. Nulstiller manuelt."},
        ],
    },
]
