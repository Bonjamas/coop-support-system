from functools import wraps
from flask import redirect
from utils.db import check_db_connection

def db_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not check_db_connection():
            return redirect("/db-error")
        return view_func(*args, **kwargs)
    return wrapper