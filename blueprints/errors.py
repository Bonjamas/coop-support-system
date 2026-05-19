import logging

from flask import Blueprint, render_template, request
from sqlalchemy.exc import OperationalError
from models import db

logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(OperationalError)
def db_down(error):
    db.session.rollback()
    logger.error("Database unavailable on %s %s: %s", request.method, request.path, error)
    return render_template("error.html", variant="db"), 503


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
def server_error(error):
    db.session.rollback()
    logger.exception("Unhandled server error on %s %s: %s", request.method, request.path, error)
    return render_template("error.html", code=500, message="Der opstod en serverfejl."), 500
