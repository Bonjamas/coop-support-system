import requests
from flask import session


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
