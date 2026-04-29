from flask import Flask, render_template, request, redirect, session
from config import Config
from models import db, Ticket
from utils.decorators import db_required
from utils.auth import build_msal_app, get_user, get_user_role
from utils.auth_decorators import login_required, role_required
from sqlalchemy import case
import os
import requests
from utils.dummy_tickets import dummy_ticket_data
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# -----------------------
# LOGIN
# -----------------------
@app.route("/login")
def login():
    auth_url = build_msal_app().get_authorization_request_url(
        ["User.Read", "User.Read.All"],
        redirect_uri="http://localhost:5000/auth/callback"
    )
    return redirect(auth_url)


@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")

    result = build_msal_app().acquire_token_by_authorization_code(
        code,
        scopes=["User.Read", "User.Read.All"],
        redirect_uri="http://localhost:5000/auth/callback"
    )

    session["user"] = result["id_token_claims"]
    session["access_token"] = result.get("access_token")

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -----------------------
# LANDING
# -----------------------
@app.route("/")
def landing():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("index.html")


# -----------------------
# DASHBOARD
# -----------------------
# 🏠 DASHBOARD (stats)
@app.route("/dashboard")
@db_required
@login_required
def home():
    role = get_user_role()

    if role == "butik":
        return redirect("/mine")

    from datetime import date
    today = date.today()

    tickets = Ticket.query.all()

    stats = {
        "created_today": len([t for t in tickets if t.created_at.date() == today]),
        "resolved_today": len([t for t in tickets if t.state == "resolved" and t.updated_at.date() == today]),
        "active": len([t for t in tickets if t.state != "resolved"]),
        "high_priority": len([t for t in tickets if t.priority == "high"]),
        "new": len([t for t in tickets if t.state == "new"]),
        "in_progress": len([t for t in tickets if t.state == "in_progress"]),
        "resolved": len([t for t in tickets if t.state == "resolved"]),
    }

    return render_template("dashboard.html", stats=stats, role=role)


# 👤 Mine (AKTIVE)
@app.route("/mine")
@db_required
@login_required
def mine():
    user = get_user()

    tickets = Ticket.query.filter(
        Ticket.assigned_to == user.get("oid"),
        Ticket.state != "resolved"
    ).order_by(Ticket.updated_at.desc()).all()

    return render_template(
        "mine.html",
        tickets=tickets,
        title="Mine aktive tickets",
        role=get_user_role()
    )


# ✅ Mine løste
@app.route("/mine/resolved")
@db_required
@login_required
def mine_resolved():
    user = get_user()

    tickets = Ticket.query.filter(
        Ticket.assigned_to == user.get("oid"),
        Ticket.state == "resolved"
    ).order_by(Ticket.updated_at.desc()).all()

    return render_template(
        "mine.html",
        tickets=tickets,
        title="Mine løste tickets",
        role=get_user_role()
    )


# 👥 FÆLLES
@app.route("/alle")
@db_required
@login_required
def alle():
    role = get_user_role()

    if role == "butik":
        return "Forbidden", 403

    tickets = Ticket.query.order_by(Ticket.updated_at.desc()).all()

    return render_template("alle.html", tickets=tickets, role=role)

# -----------------------
# VIEW / UPDATE STATUS
# -----------------------
@app.route("/ticket/<int:id>", methods=["GET", "POST"])
@db_required
@login_required
def view_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    role = get_user_role()
    user = get_user()

    # 🔒 butik må kun se egne tickets
    if role == "butik" and ticket.created_by != user.get("oid"):
        return "Forbidden", 403

    if request.method == "POST":
        action = request.form.get("action")

        # ✏️ EDIT
        if action == "edit":
            ticket.title = request.form.get("title")
            ticket.description = request.form.get("description")
            ticket.priority = request.form.get("priority")

            # ✅ FIX: beskyt state (ingen None / ugyldige værdier)
            state = request.form.get("state")
            if state in ["new", "in_progress", "resolved"]:
                ticket.state = state

            assigned_to = request.form.get("assigned_to")
            assigned_to_name = request.form.get("assigned_to_name")

            if assigned_to:
                ticket.assigned_to = assigned_to
                ticket.assigned_to_name = assigned_to_name


            requested_by = request.form.get("requested_by")
            requested_by_name = request.form.get("requested_by_name")

            if requested_by:
                ticket.requested_by = requested_by
                ticket.requested_by_name = requested_by_name

            ticket.contact_info = request.form.get("contact_info")
            ticket.type = request.form.get("type")

        # 💬 COMMENT
        elif action == "comment":
            from models import Comment

            text = request.form.get("text")
            type_ = request.form.get("type")

            if text:
                c = Comment(
                    ticket_id=ticket.id,
                    text=text,
                    author_name=user.get("name"),
                    type=type_
                )
                db.session.add(c)

                # ✅ (bevarer din tidligere intention men uden at ødelægge ting)
                if ticket.state == "new":
                    ticket.state = "in_progress"

        db.session.commit()
        return redirect(f"/ticket/{id}")

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        comments=ticket.comments,
        role=role
    )


# -----------------------
# ASSIGN
# -----------------------
@app.route("/ticket/<int:id>/assign", methods=["POST"])
@db_required
@login_required
@role_required("admin", "support")
def assign_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    ticket.assigned_to = request.form.get("assigned_to")
    ticket.assigned_to_name = request.form.get("assigned_to_name")

    db.session.commit()

    return redirect(f"/ticket/{id}")


# -----------------------
# CREATE
# -----------------------
@app.route("/create", methods=["GET", "POST"])
@db_required
@login_required
@role_required("admin", "support", "butik")
def create_ticket():
    user = get_user()

    if request.method == "POST":
        ticket = Ticket(
            title=request.form.get("title"),
            description=request.form.get("description"),
            priority=request.form.get("priority"),
            state=request.form.get("state") or "new",

            created_by=user["oid"],
            created_by_name=user["name"],

            requested_by=request.form.get("requested_by"),
            requested_by_name=request.form.get("requested_by_name"),

            assigned_to=request.form.get("assigned_to"),
            assigned_to_name=request.form.get("assigned_to_name"),
        )

        db.session.add(ticket)
        db.session.commit()

        return redirect(f"/ticket/{ticket.id}")

    return render_template("create_ticket.html")

# -----------------------
# DELETE
# -----------------------
@app.route("/ticket/<int:id>/delete", methods=["POST"])
@db_required
@login_required
@role_required("admin")
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    db.session.delete(ticket)
    db.session.commit()

    return redirect("/dashboard")

# -----------------------
# API
# -----------------------
@app.route("/api/users")
@login_required
def search_users():
    q = request.args.get("q")

    token = session.get("access_token")

    if not token:
        return []

    res = requests.get(
        "https://graph.microsoft.com/v1.0/users?$top=50",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    data = res.json()

    users = [
        {
            "name": u.get("displayName"),
            "email": u.get("mail") or u.get("userPrincipalName"),
            "oid": u.get("id")
        }
        for u in data.get("value", [])
        if q.lower() in (u.get("displayName") or "").lower()
    ]

    return users

# -----------------------
# DB ERROR
# -----------------------
@app.route("/db-error")
def db_error():
    next_url = request.args.get("next", "/")
    return render_template("db_error.html", next_url=next_url)


# -----------------------
# INIT
# -----------------------
with app.app_context():
    from utils.db import check_db_connection
    if check_db_connection():
        db.create_all()

        if os.getenv("ENV") == "development":
            dummy_ticket_data()


if __name__ == "__main__":
    app.run(debug=True)