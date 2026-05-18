import os
import msal
from flask import session
from utils.graph import graph_get

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
GRAPH_SCOPES = ["User.ReadBasic.All", "Group.Read.All"]

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


STORE_GROUP_PREFIX = "Butik - "


def store_names_from_claims(claims):
    names = []
    for group_oid in claims.get("groups") or []:
        data = graph_get(
            f"https://graph.microsoft.com/v1.0/groups/{group_oid}?$select=displayName"
        )
        if not data:
            continue
        display_name = data.get("displayName", "")
        if display_name.startswith(STORE_GROUP_PREFIX):
            names.append(display_name.removeprefix(STORE_GROUP_PREFIX))
    return names
