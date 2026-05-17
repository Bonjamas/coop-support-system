from models import Ticket, db

from . import (
    admin_nikolaj,
    support_benjamin,
    support_frederik,
    butik_greve,
    butik_hvidovre,
    butik_karlslunde,
    user_lars,
    user_mette,
    user_sofie,
    user_thomas,
)

USER_MODULES = [
    admin_nikolaj,
    support_benjamin,
    support_frederik,
    butik_karlslunde,
    butik_greve,
    butik_hvidovre,
    user_mette,
    user_lars,
    user_sofie,
    user_thomas,
]


def generate_dummy_tickets():
    if Ticket.query.first():
        return

    users = {}
    for module in USER_MODULES:
        users[module.USER["key"]] = module.USER

    count = 0
    for module in USER_MODULES:
        for ticket_data in module.TICKETS:
            _create_ticket(ticket_data, module.USER, users)
            count += 1

    db.session.commit()
    print(f"Dummy data created: {count} tickets")


def _create_ticket(ticket_data, creator, users):
    ticket = Ticket(
        title=ticket_data["title"],
        description=ticket_data["description"],
        priority=ticket_data["priority"],
        state="new",
        type=ticket_data["type"],
        contact_info=ticket_data.get("contact"),
        created_by=creator["oid"],
        created_by_name=creator["name"],
        requested_by=creator["oid"],
        requested_by_name=creator["name"],
    )
    db.session.add(ticket)
    db.session.flush()

    for event in ticket_data.get("events", []):
        actor = users[event["actor"]]
        event_type = event["event_type"]

        if event_type == "assign":
            assignee = users[event["assignee"]]
            ticket.update_assignment(assignee["oid"], assignee["name"])
        elif event_type == "note":
            ticket.add_user_comment(event["text"], "note", actor["role"], actor)
        elif event_type == "comment":
            ticket.add_user_comment(event["text"], "comment", actor["role"], actor)
        elif event_type == "resolve":
            ticket.update_state("resolved", actor["name"])
