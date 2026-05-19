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
        logger.warning("Auth callback without code: %s", dict(request.args))
        abort(400, "Login fejlede: manglende auth-kode.")

    result = build_msal_app().acquire_token_by_authorization_code(
        code,
        scopes=GRAPH_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    if "error" in result:
        message = result.get("error_description", result["error"])
        logger.error(
            "MSAL token acquisition failed: %s",
            message,
            extra={"msal_error": result.get("error")},
        )
        abort(400, f"Login fejlede: {message}")

    claims = result["id_token_claims"]
    session["access_token"] = result.get("access_token")
    session["user"] = {
        "oid": claims.get("oid"),
        "name": claims.get("name"),
        "roles": claims.get("roles", []),
        "store_names": store_names_from_claims(claims),
    }
    logger.info(
        "Login success: %s",
        claims.get("name"),
        extra={
            "user_oid": claims.get("oid"),
            "user_roles": claims.get("roles", []),
        },
    )
    return redirect(url_for("pages.index"))


@auth_bp.route("/logout")
def logout():
    user = session.get("user") or {}
    session.clear()
    logger.info(
        "Logout: %s",
        user.get("name"),
        extra={"user_oid": user.get("oid")},
    )
    return redirect(url_for("pages.index"))
