import logging
from flask import Flask
from sqlalchemy.exc import OperationalError
from werkzeug.middleware.proxy_fix import ProxyFix
from blueprints import admin_bp, auth_bp, errors_bp, pages_bp, tickets_bp
from config import Config
from models import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(tickets_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(errors_bp)


with app.app_context():
    try:
        db.create_all()
    except OperationalError as e:
        logger.error("Database unavailable at startup; skipping db.create_all: %s", e)

logger.info("App started")


if __name__ == "__main__":
    app.run(debug=True)
