from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config
from flask_migrate import Migrate
from app.blacklist import blacklist

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
   
    from app.utils import create_recurring_expenses  # Now safe to import

    def start_scheduler():
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=create_recurring_expenses, trigger="interval", hours=24)
        scheduler.start()
        app.logger.info("Scheduler started.")

    start_scheduler()

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklist

    return app
