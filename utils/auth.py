import os
import msal
from flask import session

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")
BUTIK_GROUP_ID = os.getenv("BUTIK_GROUP_ID")


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
    groups = user.get("groups", [])

    if ADMIN_GROUP_ID in groups:
        return "admin"
    elif SUPPORT_GROUP_ID in groups:
        return "support"
    elif BUTIK_GROUP_ID in groups:
        return "butik"
    return "none"