from flask import Blueprint, redirect, render_template, url_for

from models import Ticket, db
from utils.auth import get_user_role
from utils.decorators import login_required, role_required
from utils.generate_tickets import generate_dummy_tickets

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@role_required("admin")
def admin_panel():
    return render_template("admin.html", role=get_user_role())


@admin_bp.route("/admin/testdata", methods=["POST"])
@login_required
@role_required("admin")
def generate_testdata():
    generate_dummy_tickets()
    return redirect(url_for("admin.admin_panel"))


@admin_bp.route("/admin/slet-alt", methods=["POST"])
@login_required
@role_required("admin")
def delete_all_tickets():
    Ticket.query.delete()
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))
