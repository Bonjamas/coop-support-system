import os
from functools import wraps

import msal
import requests
from flask import abort, redirect, session

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
GRAPH_SCOPES = ["User.ReadBasic.All"]

ROLE_PRIORITY = ("admin", "support", "butik")
DEFAULT_ROLE = "user"


def build_msal_app():
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )


def get_user():
    return session.get("user")


def get_user_role():
    user = get_user() or {}
    roles = user.get("roles", [])
    for role in ROLE_PRIORITY:
        if role in roles:
            return role
    return DEFAULT_ROLE


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapper


def graph_get(url):
    token = session.get("access_token")
    if not token:
        return None

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    return response.json()


def resolve_user_name(oid):
    if not oid:
        return None
    data = graph_get(
        f"https://graph.microsoft.com/v1.0/users/{oid}?$select=displayName"
    )
    if not data:
        return None
    return data.get("displayName")


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if get_user_role() not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator
