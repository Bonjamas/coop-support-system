import logging
import requests
from flask import session

logger = logging.getLogger(__name__)


def graph_get(url):
    token = session.get("access_token")
    if not token:
        logger.warning("Graph call without access_token: %s", url)
        return None

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
    except requests.RequestException:
        logger.exception("Graph request failed: %s", url)
        return None

    if not response.ok:
        logger.warning(
            "Graph responded %s for %s: %s",
            response.status_code,
            url,
            response.text[:200],
        )
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


def list_users():
    data = graph_get(
        "https://graph.microsoft.com/v1.0/users"
        "?$select=id,displayName"
        "&$orderby=displayName"
        "&$top=100"
    )
    if not data:
        return []
    return [
        {"oid": u["id"], "name": u["displayName"]}
        for u in data.get("value", [])
        if u.get("id") and u.get("displayName")
    ]
