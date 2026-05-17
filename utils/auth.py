import os

import msal
from flask import session

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
GRAPH_SCOPES = ["User.ReadBasic.All"]

ROLE_PRIORITY = ("admin", "support", "butik")
DEFAULT_ROLE = "user"

STORE_SLUG_BY_AD_GROUP = {
    "a7a43b4f-7c34-49a1-a945-6d7b8bd42a42": "karlslunde",
    "6920351e-e813-428a-8c8a-9263a80a9129": "greve",
    "6eff9713-19a7-4aaf-8768-1fa9d76a3589": "hvidovre",
}

STORE_DISPLAY_NAMES = {
    "karlslunde": "SuperBrugsen Karlslunde",
    "greve":      "365discount Greve",
    "hvidovre":   "Kvickly Hvidovre",
}


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


def store_slugs_from_claims(claims):
    raw_groups = claims.get("groups") or []
    return [STORE_SLUG_BY_AD_GROUP[g] for g in raw_groups if g in STORE_SLUG_BY_AD_GROUP]


def store_names_from_claims(claims):
    return [STORE_DISPLAY_NAMES[slug] for slug in store_slugs_from_claims(claims)]
