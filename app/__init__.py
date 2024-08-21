from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
from app.config import Config
from app.blacklist import blacklist

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register the routes blueprint
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # APScheduler configuration
    def create_recurring_expenses():
        with app.app_context():
            # Import models inside the function to avoid circular imports
            from app.models import Expenses

            expenses = Expenses.query.filter(Expenses.recurrence.isnot(None)).all()
            for expense in expenses:
                if expense.recurrence == 'daily':
                    next_date = expense.date_purchase + timedelta(days=1)
                elif expense.recurrence == 'weekly':
                    next_date = expense.date_purchase + timedelta(weeks=1)
                elif expense.recurrence == 'monthly':
                    next_date = expense.date_purchase + timedelta(days=30)  # or use dateutil.relativedelta

                new_expense = Expenses(
                    type_expense=expense.type_expense,
                    description_expense=expense.description_expense,
                    date_purchase=next_date,
                    amount=expense.amount,
                    user_name=expense.user_name,
                    category_id=expense.category_id,
                    recurrence=expense.recurrence
                )
                db.session.add(new_expense)
            db.session.commit()

    def start_scheduler():
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=create_recurring_expenses, trigger="interval", hours=24)
        scheduler.start()

    start_scheduler()

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklist  # This ensures the token is checked against the blacklist

    return app
