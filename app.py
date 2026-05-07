import os
from datetime import date
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from models import Ticket, db
from utils.auth import GRAPH_SCOPES, build_msal_app, get_user, get_user_role, graph_get, login_required, resolve_user_name, role_required
from utils.db import check_db_connection
from utils.decorators import db_required
from utils.dummy_tickets import dummy_ticket_data

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
db.init_app(app)


REDIRECT_URI = os.getenv("REDIRECT_URI")

ALLOWED_PRIORITIES = {"low", "medium", "high"}
ALLOWED_TYPES = {"support", "funktionalitet", "nedbrud"}
TICKETS_PER_PAGE = 25


def _validate_choice(value, allowed, default=None):
    return value if value in allowed else default


# --- AUTH ---

@app.route("/login")
def login():
    auth_url = build_msal_app().get_authorization_request_url(
        GRAPH_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return redirect(auth_url)


@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        abort(400, "Login fejlede: manglende auth-kode.")

    result = build_msal_app().acquire_token_by_authorization_code(
        code,
        scopes=GRAPH_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    if "error" in result:
        message = result.get("error_description", result["error"])
        abort(400, f"Login fejlede: {message}")

    claims = result["id_token_claims"]
    session["user"] = {
        "oid": claims.get("oid"),
        "name": claims.get("name"),
        "roles": claims.get("roles", []),
    }
    session["access_token"] = result.get("access_token")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --- PAGES ---

@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/dashboard")
@db_required
@login_required
def dashboard():
    role = get_user_role()
    if role in ("butik", "user"):
        return redirect("/mine")

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


def _paginate(query):
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    return query.paginate(page=page, per_page=TICKETS_PER_PAGE, error_out=False)


@app.route("/mine")
@db_required
@login_required
def mine():
    role = get_user_role()
    pagination = _paginate(Ticket.for_user(get_user(), role, resolved=False))
    return render_template(
        "my_tickets.html",
        pagination=pagination,
        tickets=pagination.items,
        title="Mine aktive tickets",
        role=role,
    )


@app.route("/mine/resolved")
@db_required
@login_required
def mine_resolved():
    role = get_user_role()
    pagination = _paginate(Ticket.for_user(get_user(), role, resolved=True))
    return render_template(
        "my_tickets.html",
        pagination=pagination,
        tickets=pagination.items,
        title="Mine løste tickets",
        role=role,
    )


@app.route("/alle")
@db_required
@login_required
@role_required("admin", "support")
def alle():
    pagination = _paginate(Ticket.unassigned())
    return render_template(
        "ticket_list.html",
        pagination=pagination,
        tickets=pagination.items,
        role=get_user_role(),
        title="Fælles tickets",
    )


@app.route("/alle/alle")
@db_required
@login_required
@role_required("admin", "support")
def alle_alle():
    pagination = _paginate(Ticket.query.order_by(Ticket.updated_at.desc()))
    return render_template(
        "ticket_list.html",
        pagination=pagination,
        tickets=pagination.items,
        role=get_user_role(),
        title="Alle tickets",
    )


# --- TICKET ---

@app.route("/ticket/<int:id>", methods=["GET", "POST"])
@db_required
@login_required
def view_ticket(id):
    ticket = Ticket.query.get_or_404(id)
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

            ticket.title = title
            ticket.description = request.form.get("description")
            ticket.priority = _validate_choice(
                request.form.get("priority"), ALLOWED_PRIORITIES, ticket.priority
            )
            ticket.contact_info = request.form.get("contact_info")
            ticket.type = _validate_choice(
                request.form.get("type"), ALLOWED_TYPES, ticket.type
            )
            ticket.update_state(
                request.form.get("state"), user.get("name")
            )
            new_assigned = request.form.get("assigned_to")
            if new_assigned and new_assigned != ticket.assigned_to:
                new_assigned_name = resolve_user_name(new_assigned)
            else:
                new_assigned_name = ticket.assigned_to_name
            ticket.update_assignment(new_assigned, new_assigned_name, user)

            new_requested = request.form.get("requested_by")
            if new_requested and new_requested != ticket.requested_by:
                new_requested_name = resolve_user_name(new_requested)
            else:
                new_requested_name = ticket.requested_by_name
            ticket.update_requested_by(new_requested, new_requested_name)

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
                comment_type = _validate_choice(
                    request.form.get("type"), allowed, default="comment"
                )
                ticket.add_user_comment(text, comment_type, role, user)

        else:
            abort(400, "Ugyldig handling.")

        db.session.commit()
        return redirect(f"/ticket/{id}")

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        role=role,
    )


@app.route("/create", methods=["GET", "POST"])
@db_required
@login_required
def create_ticket():
    user = get_user()
    role = get_user_role()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            abort(400, "Titel er påkrævet.")

        priority = _validate_choice(
            request.form.get("priority"), ALLOWED_PRIORITIES, default="medium"
        )
        ticket_type = _validate_choice(
            request.form.get("type"), ALLOWED_TYPES, default="support"
        )

        if role in ("butik", "user"):
            requested_by = user["oid"]
            requested_by_name = user["name"]
            assigned_to = None
            assigned_to_name = None
        else:
            requested_by = request.form.get("requested_by")
            if not requested_by:
                abort(400, "Anmodet af er påkrævet.")
            requested_by_name = resolve_user_name(requested_by)
            assigned_to = request.form.get("assigned_to")
            assigned_to_name = resolve_user_name(assigned_to)

        ticket = Ticket(
            title=title,
            description=request.form.get("description"),
            priority=priority,
            state="new",
            type=ticket_type,
            contact_info=request.form.get("contact_info"),
            created_by=user["oid"],
            created_by_name=user["name"],
            requested_by=requested_by,
            requested_by_name=requested_by_name,
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name,
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect(f"/ticket/{ticket.id}")

    return render_template("create_ticket.html", role=role)


@app.route("/ticket/<int:id>/delete", methods=["POST"])
@db_required
@login_required
@role_required("admin")
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    return redirect("/dashboard")


# --- API ---

@app.route("/api/users")
@login_required
@role_required("admin", "support")
def search_users():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    escaped = query.replace("'", "''")
    encoded = quote(escaped, safe="")
    url = (
        "https://graph.microsoft.com/v1.0/users"
        f"?$filter=startswith(displayName,'{encoded}')"
        "&$select=id,displayName,mail,userPrincipalName"
        "&$top=10"
    )

    data = graph_get(url)
    if data is None:
        return jsonify({"error": "graph_unavailable"}), 502

    return jsonify([
        {
            "name": u.get("displayName"),
            "email": u.get("mail") or u.get("userPrincipalName"),
            "oid": u.get("id"),
        }
        for u in data.get("value", [])
        if u.get("displayName")
    ])


# --- ADMIN ---

@app.route("/admin")
@db_required
@login_required
@role_required("admin")
def admin_panel():
    return render_template("admin.html", role=get_user_role())


@app.route("/admin/testdata", methods=["POST"])
@db_required
@login_required
@role_required("admin")
def seed_data():
    dummy_ticket_data()
    return redirect(url_for("admin_panel"))


@app.route("/admin/slet-alt", methods=["POST"])
@db_required
@login_required
@role_required("admin")
def delete_all():
    Ticket.query.delete()
    db.session.commit()
    return redirect(url_for("admin_panel"))


# --- ERRORS ---

@app.route("/db-error")
def db_error():
    return render_template("db_error.html")


@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message="Siden findes ikke."), 404


@app.errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, message="Du har ikke adgang."), 403


@app.errorhandler(400)
def bad_request(e):
    msg = getattr(e, "description", "Ugyldig forespørgsel.")
    return render_template("error.html", code=400, message=msg), 400


@app.errorhandler(500)
def server_error(_):
    db.session.rollback()
    return render_template("error.html", code=500, message="Der opstod en serverfejl."), 500


with app.app_context():
    if check_db_connection():
        db.create_all()


if __name__ == "__main__":
    app.run(debug=True)