from datetime import date
from flask import Blueprint, redirect, render_template, session, url_for
from models import Ticket
from utils.auth import get_user, get_user_role
from utils.decorators import login_required, role_required
from utils.listing import build_listing, query_args
from utils.sort import current_sort

pages_bp = Blueprint("pages", __name__)


@pages_bp.app_context_processor
def inject_listing_state():
    sort, order = current_sort()
    return {
        "query_args": query_args,
        "current_sort": sort,
        "current_order": order,
    }


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
    pagination = build_listing(Ticket.for_user(get_user(), role, resolved=False))
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
    pagination = build_listing(Ticket.for_user(get_user(), role, resolved=True))
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
    pagination = build_listing(Ticket.unassigned())
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
    pagination = build_listing(Ticket.query)
    return render_template(
        "ticket_list.html",
        pagination=pagination,
        tickets=pagination.items,
        role=get_user_role(),
        title="Alle tickets",
    )
