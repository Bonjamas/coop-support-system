from functools import wraps
from flask import session, redirect
from utils.auth import get_user_role


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role = get_user_role()

            if role not in roles:
                return "Forbidden", 403

            return f(*args, **kwargs)
        return wrapper
    return decorator