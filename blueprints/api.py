from urllib.parse import quote

from flask import Blueprint, jsonify, request

from utils.decorators import login_required, role_required
from utils.graph import graph_get

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/users")
@login_required
@role_required("admin", "support")
def search_users():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    escaped = query.replace("'", "''")
    encoded = quote(escaped, safe="")
    url = (
        "https://graph.microsoft.com/v1.0/users"
        f"?$filter=startswith(displayName,'{encoded}')"
        "&$select=id,displayName,mail,userPrincipalName"
        "&$top=10"
    )

    data = graph_get(url)
    if data is None:
        return jsonify({"error": "graph_unavailable"}), 502

    return jsonify([
        {
            "name": u.get("displayName"),
            "email": u.get("mail") or u.get("userPrincipalName"),
            "oid": u.get("id"),
        }
        for u in data.get("value", [])
        if u.get("displayName")
    ])
