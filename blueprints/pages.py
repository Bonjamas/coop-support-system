from datetime import date

from flask import Blueprint, redirect, render_template, request, session, url_for
from sqlalchemy import case

from models import Ticket
from utils.auth import get_user, get_user_role
from utils.decorators import login_required, role_required

pages_bp = Blueprint("pages", __name__)

TICKETS_PER_PAGE = 25

SORT_COLUMNS = {
    "id": Ticket.id,
    "title": Ticket.title,
    "type": Ticket.type,
    "requested": Ticket.requested_by_name,
    "assigned": Ticket.assigned_to_name,
    "created": Ticket.created_at,
    "updated": Ticket.updated_at,
}


def _priority_sort_value():
    return case(
        (Ticket.priority == "high", 3),
        (Ticket.priority == "medium", 2),
        (Ticket.priority == "low", 1),
        else_=0,
    )


def _state_sort_value():
    return case(
        (Ticket.state == "new", 1),
        (Ticket.state == "in_progress", 2),
        (Ticket.state == "resolved", 3),
        else_=0,
    )


def _sort_expression():
    sort = request.args.get("sort", "updated")
    order = request.args.get("order", "desc")
    if sort == "priority":
        column = _priority_sort_value()
    elif sort == "state":
        column = _state_sort_value()
    else:
        column = SORT_COLUMNS.get(sort, Ticket.updated_at)
    return column.desc() if order == "desc" else column.asc()


def _search_filter():
    search_term = (request.args.get("q") or "").strip()
    if not search_term:
        return None
    pattern = f"%{search_term}%"
    return (
        Ticket.title.ilike(pattern)
        | Ticket.requested_by_name.ilike(pattern)
        | Ticket.assigned_to_name.ilike(pattern)
    )


def _build_listing(query):
    if (search_clause := _search_filter()) is not None:
        query = query.filter(search_clause)
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    return query.order_by(_sort_expression()).paginate(
        page=page, per_page=TICKETS_PER_PAGE, error_out=False
    )


@pages_bp.app_context_processor
def inject_query_args():
    def query_args(**overrides):
        args = request.args.to_dict()
        args.update(overrides)
        return args
    return {"query_args": query_args}


@pages_bp.route("/")
def index():
    if "user" in session:
        return redirect(url_for("pages.dashboard"))
    return render_template("index.html")


@pages_bp.route("/dashboard")
@login_required
def dashboard():
    role = get_user_role()
    if role in ("butik", "user"):
        return redirect(url_for("pages.mine"))

    today = date.today()
    tickets = Ticket.query.all()

    stats = {
        "created_today": sum(
            1 for t in tickets if t.created_at.date() == today
        ),
        "resolved_today": sum(
            1 for t in tickets
            if t.state == "resolved" and t.updated_at.date() == today
        ),
        "active": sum(1 for t in tickets if t.state != "resolved"),
        "high_priority": sum(1 for t in tickets if t.priority == "high"),
        "new": sum(1 for t in tickets if t.state == "new"),
        "in_progress": sum(1 for t in tickets if t.state == "in_progress"),
        "resolved": sum(1 for t in tickets if t.state == "resolved"),
    }
    return render_template("dashboard.html", stats=stats, role=role)


@pages_bp.route("/mine")
@login_required
def mine():
    role = get_user_role()
    pagination = _build_listing(Ticket.for_user(get_user(), role, resolved=False))
    return render_template(
        "my_tickets.html",
        pagination=pagination,
        tickets=pagination.items,
        title="Mine aktive tickets",
        role=role,
    )


@pages_bp.route("/mine/resolved")
@login_required
def mine_resolved():
    role = get_user_role()
    pagination = _build_listing(Ticket.for_user(get_user(), role, resolved=True))
    return render_template(
        "my_tickets.html",
        pagination=pagination,
        tickets=pagination.items,
        title="Mine løste tickets",
        role=role,
    )


@pages_bp.route("/alle")
@login_required
@role_required("admin", "support")
def alle():
    pagination = _build_listing(Ticket.unassigned())
    return render_template(
        "ticket_list.html",
        pagination=pagination,
        tickets=pagination.items,
        role=get_user_role(),
        title="Fælles tickets",
    )


@pages_bp.route("/alle/alle")
@login_required
@role_required("admin", "support")
def alle_alle():
    pagination = _build_listing(Ticket.query)
    return render_template(
        "ticket_list.html",
        pagination=pagination,
        tickets=pagination.items,
        role=get_user_role(),
        title="Alle tickets",
    )
