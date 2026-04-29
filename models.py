from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 🧾 Core
    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    # 🔥 ServiceNow style
    priority = db.Column(db.String(20), default="medium")  # low / medium / high
    state = db.Column(db.String(20), default="new")  # new / in_progress / resolved

    # 👤 Opened by
    created_by = db.Column(db.String(100))
    created_by_name = db.Column(db.String(100))

    # 👤 Requested by
    requested_by = db.Column(db.String(100))
    requested_by_name = db.Column(db.String(100))

    # 🛠 Assigned to
    assigned_to = db.Column(db.String(100))
    assigned_to_name = db.Column(db.String(100))

    # 📞 Extra
    contact_info = db.Column(db.String(100))
    type = db.Column(db.String(50))  # support / funktionalitet / nedbrud

    # ⏱ Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 💬 Relation
    comments = db.relationship(
        "Comment",
        backref="ticket",
        lazy=True,
        cascade="all, delete"
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ticket.id"),
        nullable=False
    )

    text = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100))
    type = db.Column(db.String(20))  # comment / note

    created_at = db.Column(db.DateTime, default=datetime.utcnow)