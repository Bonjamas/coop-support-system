from flask import request
from models import Ticket


def apply_search(query):
    term = (request.args.get("q") or "").strip()
    if not term:
        return query
    pattern = f"%{term}%"
    return query.filter(
        Ticket.title.ilike(pattern)
        | Ticket.requested_by_name.ilike(pattern)
        | Ticket.assigned_to_name.ilike(pattern)
    )
