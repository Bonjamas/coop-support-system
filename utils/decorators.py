from functools import wraps

from flask import abort, redirect, session, url_for

from utils.auth import get_user_role


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if get_user_role() not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator
