from flask import Blueprint, abort, redirect, render_template, request, url_for

from models import Ticket, db
from utils.auth import get_user, get_user_role
from utils.decorators import login_required, role_required
from utils.graph import list_users, resolve_user_name

tickets_bp = Blueprint("tickets", __name__)

ALLOWED_PRIORITIES = {"low", "medium", "high"}
ALLOWED_TYPES = {"support", "funktionalitet", "nedbrud"}


@tickets_bp.route("/ticket/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    role = get_user_role()
    user = get_user()

    if role in ("butik", "user") and ticket.created_by != user.get("oid"):
        abort(403)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "edit":
            if role not in ("admin", "support"):
                abort(403)

            title = (request.form.get("title") or "").strip()
            if not title:
                abort(400, "Titel er påkrævet.")

            ticket.update_title(title, user)
            ticket.description = request.form.get("description")
            ticket.update_priority(request.form.get("priority"), user)
            ticket.contact_info = request.form.get("contact_info")
            ticket.update_type(request.form.get("type"), user)
            ticket.update_state(request.form.get("state"), user)

            new_assigned_oid = request.form.get("assigned_to")
            if new_assigned_oid and new_assigned_oid != ticket.assigned_to:
                new_assigned_name = resolve_user_name(new_assigned_oid)
            else:
                new_assigned_name = ticket.assigned_to_name
            ticket.update_assignment(new_assigned_oid, new_assigned_name, user)

            new_requested_oid = request.form.get("requested_by")
            if new_requested_oid and new_requested_oid != ticket.requested_by:
                new_requested_name = resolve_user_name(new_requested_oid)
            else:
                new_requested_name = ticket.requested_by_name
            ticket.update_requested_by(new_requested_oid, new_requested_name, user)

        elif action == "resolve":
            if role not in ("admin", "support"):
                abort(403)
            ticket.update_state("resolved", user)

        elif action == "close":
            if role not in ("butik", "user") or ticket.created_by != user.get("oid"):
                abort(403)
            ticket.close_by(user)

        elif action == "comment":
            text = (request.form.get("text") or "").strip()
            if text:
                allowed = (
                    {"comment", "note"}
                    if role in ("admin", "support")
                    else {"comment"}
                )
                comment_type = request.form.get("type")
                if comment_type not in allowed:
                    comment_type = "comment"
                ticket.add_user_comment(text, comment_type, role, user)

        else:
            abort(400, "Ugyldig handling.")

        db.session.commit()
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket_id))

    users = list_users() if role in ("admin", "support") else []
    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        role=role,
        users=users,
    )


@tickets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    user = get_user()
    role = get_user_role()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            abort(400, "Titel er påkrævet.")

        priority = request.form.get("priority")
        if priority not in ALLOWED_PRIORITIES:
            priority = "medium"
        ticket_type = request.form.get("type")
        if ticket_type not in ALLOWED_TYPES:
            ticket_type = "support"

        if role in ("butik", "user"):
            requested_by_oid = user["oid"]
            requested_by_name = user["name"]
            assigned_to_oid = None
            assigned_to_name = None
        else:
            requested_by_oid = request.form.get("requested_by")
            if not requested_by_oid:
                abort(400, "Anmodet af er påkrævet.")
            requested_by_name = resolve_user_name(requested_by_oid)
            assigned_to_oid = request.form.get("assigned_to") or None
            assigned_to_name = resolve_user_name(assigned_to_oid) if assigned_to_oid else None

        ticket = Ticket(
            title=title,
            description=request.form.get("description"),
            priority=priority,
            state="new",
            type=ticket_type,
            contact_info=request.form.get("contact_info"),
            created_by=user["oid"],
            created_by_name=user["name"],
            requested_by=requested_by_oid,
            requested_by_name=requested_by_name,
            assigned_to=assigned_to_oid,
            assigned_to_name=assigned_to_name,
        )
        db.session.add(ticket)
        db.session.flush()
        ticket.log_creation(user)
        db.session.commit()
        return redirect(url_for("tickets.view_ticket", ticket_id=ticket.id))

    users = list_users() if role in ("admin", "support") else []
    return render_template("create_ticket.html", role=role, users=users)


@tickets_bp.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return redirect(url_for("pages.dashboard"))
