import logging
import os
from flask import Blueprint, abort, redirect, request, session, url_for
from utils.auth import GRAPH_SCOPES, build_msal_app, store_names_from_claims

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

REDIRECT_URI = os.getenv("REDIRECT_URI")


@auth_bp.route("/login")
def login():
    auth_url = build_msal_app().get_authorization_request_url(
        GRAPH_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return redirect(auth_url)


@auth_bp.route("/auth/callback")
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
        logger.error("MSAL token acquisition failed: %s", message)
        abort(400, f"Login fejlede: {message}")

    claims = result["id_token_claims"]
    session["access_token"] = result.get("access_token")
    session["user"] = {
        "oid": claims.get("oid"),
        "name": claims.get("name"),
        "roles": claims.get("roles", []),
        "store_names": store_names_from_claims(claims),
    }
    return redirect(url_for("pages.index"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("pages.index"))
