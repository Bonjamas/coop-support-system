from sqlalchemy import text
from models import db

def check_db_connection():
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except Exception:
        db.session.rollback()
        return False