from flask import request, session
from sqlalchemy import case
from models import Ticket

DEFAULT_SORT = "updated"
DEFAULT_ORDER = "desc"

SORT_COLUMNS = {
    "id": Ticket.id,
    "title": Ticket.title,
    "type": Ticket.type,
    "priority": case(
        (Ticket.priority == "high", 3),
        (Ticket.priority == "medium", 2),
        (Ticket.priority == "low", 1),
        else_=0,
    ),
    "requested": Ticket.requested_by_name,
    "assigned": Ticket.assigned_to_name,
    "state": case(
        (Ticket.state == "new", 1),
        (Ticket.state == "in_progress", 2),
        (Ticket.state == "resolved", 3),
        else_=0,
    ),
    "created": Ticket.created_at,
    "updated": Ticket.updated_at,
}


def current_sort():
    if "sort" in request.args:
        session["sort"] = request.args.get("sort")
        session["order"] = request.args.get("order", DEFAULT_ORDER)
    return (
        session.get("sort", DEFAULT_SORT),
        session.get("order", DEFAULT_ORDER),
    )


def apply_sort(query):
    sort, order = current_sort()
    column = SORT_COLUMNS.get(sort, Ticket.updated_at)
    return query.order_by(column.desc() if order == "desc" else column.asc())
