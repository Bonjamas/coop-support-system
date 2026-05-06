from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

END_USER_ROLES = ("butik", "user")


class Ticket(db.Model):
    STATE_LABELS = {
        "new": "Ny",
        "in_progress": "I gang",
        "resolved": "Løst",
    }

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    priority = db.Column(db.String(20), default="medium")
    state = db.Column(db.String(20), default="new")

    created_by = db.Column(db.String(100))
    created_by_name = db.Column(db.String(100))

    requested_by = db.Column(db.String(100))
    requested_by_name = db.Column(db.String(100))

    assigned_to = db.Column(db.String(100))
    assigned_to_name = db.Column(db.String(100))

    contact_info = db.Column(db.String(100))
    type = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    comments = db.relationship(
        "Comment",
        backref="ticket",
        lazy=True,
        cascade="all, delete",
    )

    @classmethod
    def for_user(cls, user, role, resolved=False):
        owner_field = (
            cls.created_by if role in END_USER_ROLES else cls.assigned_to
        )
        if resolved:
            state_filter = cls.state == "resolved"
        else:
            state_filter = cls.state != "resolved"
        return (
            cls.query
            .filter(owner_field == user.get("oid"), state_filter)
            .order_by(cls.updated_at.desc())
        )

    @classmethod
    def unassigned(cls):
        return (
            cls.query
            .filter((cls.assigned_to.is_(None)) | (cls.assigned_to == ""))
            .order_by(cls.updated_at.desc())
        )

    def update_state(self, new_state, actor_name):
        if new_state not in self.STATE_LABELS or new_state == self.state:
            return
        label = self.STATE_LABELS[new_state]
        db.session.add(Comment.system_internal(
            self.id,
            f'Tilstand ændret til "{label}" af {actor_name}.',
        ))
        self.state = new_state

    def update_assignment(self, new_oid, new_name, current_user):
        new_oid = (new_oid or "").strip()
        previous_oid = self.assigned_to

        if new_oid:
            self.assigned_to = new_oid
            self.assigned_to_name = new_name
            if new_oid != previous_oid:
                db.session.add(Comment.system(
                    self.id, f"Tildelt til {new_name}."
                ))
        elif not previous_oid:
            self.assigned_to = current_user.get("oid")
            self.assigned_to_name = current_user.get("name")
            db.session.add(Comment.system(
                self.id, f"Tildelt til {self.assigned_to_name}."
            ))
        else:
            self.assigned_to = None
            self.assigned_to_name = None
            db.session.add(Comment.system(self.id, "Tildeling fjernet."))

    def update_requested_by(self, new_oid, new_name):
        if new_oid:
            self.requested_by = new_oid
            self.requested_by_name = new_name

    def close_by(self, user):
        self.state = "resolved"
        db.session.add(Comment.system(
            self.id, f"Ticket lukket af {user.get('name')}."
        ))

    def add_user_comment(self, text, comment_type, role, user):
        db.session.add(Comment(
            ticket_id=self.id,
            text=text,
            author_oid=user.get("oid"),
            author_name=user.get("name"),
            type=comment_type,
        ))
        if role in END_USER_ROLES and self.state == "resolved":
            self.state = "in_progress"
            db.session.add(Comment.system(
                self.id, f"Ticket genåbnet af {user.get('name')}."
            ))
        elif self.state == "new":
            self.state = "in_progress"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("ticket.id"), nullable=False
    )

    text = db.Column(db.Text, nullable=False)
    author_oid = db.Column(db.String(100))
    author_name = db.Column(db.String(100))
    type = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def system(cls, ticket_id, text):
        return cls(
            ticket_id=ticket_id,
            text=text,
            author_name="System",
            type="system",
        )

    @classmethod
    def system_internal(cls, ticket_id, text):
        return cls(
            ticket_id=ticket_id,
            text=text,
            author_name="System",
            type="system_internal",
        )
