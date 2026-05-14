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
            {"event_type": "assign", "udfører": "support2", "assignee": "support2"},
            {"event_type": "comment", "udfører": "lars", "text": "Jeg har tjekket spam-mappen — der er ikke noget nulstillingsmail."},
            {"event_type": "note", "udfører": "support2", "text": "Nulstillingsmailen ryger i spam pga. manglende SPF-record på vores mailserver. Nulstiller manuelt."},
        ],
    },
]
