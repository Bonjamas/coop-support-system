from models import db, Ticket

def dummy_ticket_data():
    if Ticket.query.first():
        return

    print("opretter dummy tickets...")

    dummy_tickets = [
        Ticket(
            title="Nulstil password til medarbejder",
            description="Butiksmedarbejder kan ikke logge ind på systemet",
            priority="medium",
            status="open"
        ),
        Ticket(
            title="Kasse 3 genstarter konstant",
            description="Kassen fryser og genstarter flere gange dagligt",
            priority="high",
            status="open"
        ),
        Ticket(
            title="Printer virker ikke",
            description="Bon printer i butik udskriver ikke kvitteringer",
            priority="low",
            status="open"
        ),
        Ticket(
            title="Netværk nede i butik",
            description="Ingen forbindelse til interne systemer",
            priority="high",
            status="closed"
        ),
        Ticket(
            title="Scanner virker ikke",
            description="Stregkodescanner reagerer ikke",
            priority="medium",
            status="open"
        ),
    ]

    db.session.add_all(dummy_tickets)
    db.session.commit()

    print("Dummy tickets oprettet")