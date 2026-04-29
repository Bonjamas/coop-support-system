from models import db, Ticket

def dummy_ticket_data():
    if Ticket.query.first():
        return

    print("Opretter dummy tickets...")

    USERS = {
        "admin": {
            "oid": "a59ecfe8-c8b2-4f6c-a760-980a914c7177",
            "name": "Nikolaj Admin"
        },
        "support1": {
            "oid": "c5b64939-3ba3-4352-aa68-419f453e7b3b",
            "name": "Benjamin Support"
        },
        "support2": {
            "oid": "1097ed99-44ee-4a1b-8423-88fde4b5eb5f",
            "name": "Frederik Support"
        },
        "karlslunde": {
            "oid": "28ecb256-770c-4d8b-830f-68d936b1c96b",
            "name": "SuperBrugsen Karlslunde"
        },
        "greve": {
            "oid": "7a38f75b-a896-499d-89d6-579cb367314d",
            "name": "365discount Greve"
        },
        "hvidovre": {
            "oid": "3e2718de-6ead-4a85-9293-9f628722bf26",
            "name": "Kvickly Hvidovre"
        },
    }

    tickets = [

        # 🔴 Nedbrud
        Ticket(
            title="Kasse 2 fryser",
            description="Kassen går i stå flere gange dagligt",
            priority="high",
            state="new",
            type="nedbrud",
            contact_info="karlslunde@coop.dk",
            created_by=USERS["karlslunde"]["oid"],
            created_by_name=USERS["karlslunde"]["name"],
            requested_by=USERS["karlslunde"]["oid"],
            requested_by_name=USERS["karlslunde"]["name"],
            assigned_to=USERS["support1"]["oid"],
            assigned_to_name=USERS["support1"]["name"]
        ),

        Ticket(
            title="Netværk nede",
            description="Ingen forbindelse til systemer",
            priority="high",
            state="in_progress",
            type="nedbrud",
            contact_info="greve@coop.dk",
            created_by=USERS["greve"]["oid"],
            created_by_name=USERS["greve"]["name"],
            requested_by=USERS["greve"]["oid"],
            requested_by_name=USERS["greve"]["name"],
            assigned_to=USERS["support2"]["oid"],
            assigned_to_name=USERS["support2"]["name"]
        ),

        # 🟡 Support
        Ticket(
            title="Login virker ikke",
            description="Medarbejder kan ikke logge ind",
            priority="medium",
            state="new",
            type="support",
            contact_info="hvidovre@coop.dk",
            created_by=USERS["hvidovre"]["oid"],
            created_by_name=USERS["hvidovre"]["name"],
            requested_by=USERS["hvidovre"]["oid"],
            requested_by_name=USERS["hvidovre"]["name"],
            assigned_to=USERS["support1"]["oid"],
            assigned_to_name=USERS["support1"]["name"]
        ),

        Ticket(
            title="Printer virker ikke",
            description="Bon printer reagerer ikke",
            priority="medium",
            state="resolved",
            type="support",
            contact_info="karlslunde@coop.dk",
            created_by=USERS["karlslunde"]["oid"],
            created_by_name=USERS["karlslunde"]["name"],
            requested_by=USERS["karlslunde"]["oid"],
            requested_by_name=USERS["karlslunde"]["name"],
            assigned_to=USERS["support2"]["oid"],
            assigned_to_name=USERS["support2"]["name"]
        ),

        # 🟢 Funktionalitet
        Ticket(
            title="Scanner virker ikke",
            description="Stregkoder kan ikke læses",
            priority="low",
            state="new",
            type="funktionalitet",
            contact_info="greve@coop.dk",
            created_by=USERS["greve"]["oid"],
            created_by_name=USERS["greve"]["name"],
            requested_by=USERS["greve"]["oid"],
            requested_by_name=USERS["greve"]["name"],
            assigned_to=USERS["support1"]["oid"],
            assigned_to_name=USERS["support1"]["name"]
        ),

        Ticket(
            title="POS terminal genstarter",
            description="Terminal genstarter spontant",
            priority="high",
            state="in_progress",
            type="nedbrud",
            contact_info="hvidovre@coop.dk",
            created_by=USERS["hvidovre"]["oid"],
            created_by_name=USERS["hvidovre"]["name"],
            requested_by=USERS["hvidovre"]["oid"],
            requested_by_name=USERS["hvidovre"]["name"],
            assigned_to=USERS["support2"]["oid"],
            assigned_to_name=USERS["support2"]["name"]
        ),

        # 👑 Admin
        Ticket(
            title="Database vedligehold",
            description="Planlagt maintenance",
            priority="low",
            state="new",
            type="funktionalitet",
            contact_info="admin@coop.dk",
            created_by=USERS["admin"]["oid"],
            created_by_name=USERS["admin"]["name"],
            requested_by=USERS["admin"]["oid"],
            requested_by_name=USERS["admin"]["name"],
            assigned_to=USERS["support1"]["oid"],
            assigned_to_name=USERS["support1"]["name"]
        ),
    ]

    db.session.add_all(tickets)
    db.session.commit()

    print("Dummy data oprettet ✔")