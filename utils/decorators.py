from functools import wraps

from flask import redirect, url_for

from utils.db import check_db_connection


def db_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not check_db_connection():
            return redirect(url_for("db_error"))
        return view(*args, **kwargs)
    return wrapper
