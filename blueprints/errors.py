from flask import Blueprint, render_template

from models import db

errors_bp = Blueprint("errors", __name__)


@errors_bp.route("/db-error")
def db_error():
    return render_template("db_error.html")


@errors_bp.app_errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message="Siden findes ikke."), 404


@errors_bp.app_errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, message="Du har ikke adgang."), 403


@errors_bp.app_errorhandler(400)
def bad_request(e):
    msg = getattr(e, "description", "Ugyldig forespørgsel.")
    return render_template("error.html", code=400, message=msg), 400


@errors_bp.app_errorhandler(500)
def server_error(_):
    db.session.rollback()
    return render_template("error.html", code=500, message="Der opstod en serverfejl."), 500
