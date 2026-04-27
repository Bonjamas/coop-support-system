from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import time
from models import db

def check_db_connection(retries=3, delay=2):
    for i in range(retries):
        try:
            db.session.execute(text("SELECT 1"))
            return True
        except OperationalError:
            print(f"DB failed attempt {i+1}")
            time.sleep(delay)
    return False