from functools import wraps
from flask import redirect, url_for, request
from utils.db import check_db_connection

def db_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_db_connection():
            return redirect(url_for("db_error", next=request.path))
        return f(*args, **kwargs)
    return decorated