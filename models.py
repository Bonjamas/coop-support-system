from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

END_USER_ROLES = ("butik", "user")


def _utcnow():
    return datetime.now(timezone.utc)


class Ticket(db.Model):
    STATE_LABELS = {
        "new": "Ny",
        "in_progress": "I gang",
        "resolved": "Løst",
    }

    # --- COLUMNS ---
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    priority = db.Column(db.String(20), default="medium", nullable=False)
    state = db.Column(db.String(20), default="new", nullable=False, index=True)

    created_by = db.Column(db.String(100), nullable=False, index=True)
    created_by_name = db.Column(db.String(100), nullable=False)

    requested_by = db.Column(db.String(100), nullable=False)
    requested_by_name = db.Column(db.String(100), nullable=False)

    assigned_to = db.Column(db.String(100), index=True)
    assigned_to_name = db.Column(db.String(100))

    contact_info = db.Column(db.String(100))
    type = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    comments = db.relationship("Comment", backref="ticket", lazy=True, cascade="all, delete-orphan", passive_deletes=True)

    # --- QUERIES ---
    @classmethod
    def for_user(cls, user, role, resolved=False):
        owner_field = (
            cls.created_by if role in END_USER_ROLES else cls.assigned_to
        )
        state_filter = (
            cls.state == "resolved" if resolved else cls.state != "resolved"
        )
        return cls.query.filter(owner_field == user.get("oid"), state_filter)

    @classmethod
    def unassigned(cls):
        return cls.query.filter(
            (cls.assigned_to.is_(None)) | (cls.assigned_to == "")
        )

    # --- MUTATIONS ---
    def update_state(self, new_state, actor_name):
        if new_state not in self.STATE_LABELS or new_state == self.state:
            return
        label = self.STATE_LABELS[new_state]
        db.session.add(Comment.system_internal(
            f'Tilstand ændret til "{label}" af {actor_name}.',
            ticket_id=self.id,
        ))
        self.state = new_state

    def update_assignment(self, new_oid, new_name):
        new_oid = (new_oid or "").strip()
        previous_oid = self.assigned_to

        if new_oid:
            self.assigned_to = new_oid
            self.assigned_to_name = new_name
            if new_oid != previous_oid:
                db.session.add(Comment.system(
                    f"Tildelt til {new_name}.", ticket_id=self.id
                ))
        elif previous_oid:
            self.assigned_to = None
            self.assigned_to_name = None
            db.session.add(Comment.system("Tildeling fjernet.", ticket_id=self.id))

    def update_requested_by(self, new_oid, new_name):
        if new_oid:
            self.requested_by = new_oid
            self.requested_by_name = new_name

    def close_by(self, user):
        self.state = "resolved"
        db.session.add(Comment.system(
            f"Ticket lukket af {user.get('name')}.", ticket_id=self.id
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
                f"Ticket genåbnet af {user.get('name')}.", ticket_id=self.id
            ))
        elif self.state == "new":
            self.state = "in_progress"


class Comment(db.Model):
    # --- COLUMNS ---
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("ticket.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    text = db.Column(db.Text, nullable=False)
    author_oid = db.Column(db.String(100))
    author_name = db.Column(db.String(100))
    type = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)

    # --- FACTORIES ---
    @classmethod
    def system(cls, text, ticket_id=None):
        return cls(
            ticket_id=ticket_id,
            text=text,
            author_name="System",
            type="system",
        )

    @classmethod
    def system_internal(cls, text, ticket_id=None):
        return cls(
            ticket_id=ticket_id,
            text=text,
            author_name="System",
            type="system_internal",
        )
