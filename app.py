from flask import Flask, render_template, request, redirect, session
from config import Config
from models import db, Ticket
from utils.decorators import db_required
from utils.db import check_db_connection
from sqlalchemy import case
import os
from utils.dummy_tickets import dummy_ticket_data

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# -----------------------
# HOME = DASHBOARD
# -----------------------
@app.route("/")
@db_required
def home():
    sort = request.args.get("sort") or session.get("sort") or "updated"
    order = request.args.get("order") or session.get("order") or "desc"

    session["sort"] = sort
    session["order"] = order

    column_map = {
        "id": Ticket.id,
        "title": Ticket.title,
        "status": Ticket.status,
        "created": Ticket.created_at,
        "updated": Ticket.updated_at
    }

    if sort == "priority":
        column = case(
            (Ticket.priority == "low", 1),
            (Ticket.priority == "medium", 2),
            (Ticket.priority == "high", 3),
            else_=4
        )
    else:
        column = column_map.get(sort, Ticket.updated_at)

    if order == "desc":
        column = column.desc()

    tickets = Ticket.query.order_by(column).all()

    return render_template(
        "dashboard.html",
        tickets=tickets,
        sort=sort,
        order=order
    )


# -----------------------
# VIEW + UPDATE TICKET
# -----------------------
@app.route("/ticket/<int:id>", methods=["GET", "POST"])
@db_required
def view_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "close":
            ticket.status = "closed"
            db.session.commit()
            return redirect("/")

        elif action == "open":
            ticket.status = "open"
            db.session.commit()
            return redirect(f"/ticket/{id}")

    return render_template("ticket_detail.html", ticket=ticket)


# -----------------------
# CREATE & DELETE
# -----------------------
@app.route("/create", methods=["GET", "POST"])
@db_required
def create_ticket():
    if request.method == "POST":
        ticket = Ticket(
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form["priority"]
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect("/")

    return render_template("create_ticket.html")

@app.route("/ticket/<int:id>/delete", methods=["POST"])
@db_required
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    db.session.delete(ticket)
    db.session.commit()

    return redirect("/")


# -----------------------
# DB INIT
# -----------------------
with app.app_context():
    if check_db_connection():
        db.create_all()

        if os.getenv("ENV") == "development":
            dummy_ticket_data()


if __name__ == "__main__":
    app.run(debug=True)