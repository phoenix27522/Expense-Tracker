from werkzeug.security import check_password_hash
from flask import current_app as app  # Ensure you're in the app context

def verify_user_credentials(email, password):
    from app.models import User  # Import inside the function to avoid circular imports
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def create_notification(user_id, message, notif_type):
    from app.models import Notification, db  # Import inside the function to avoid circular imports
    notification = Notification(user_id=user_id, message=message, type=notif_type)
    db.session.add(notification)
    db.session.commit()

def check_for_large_expense(expense):
    from app.models import db  # Import inside the function to avoid circular imports
    threshold = 1000
    if expense.amount >= threshold:
        message = f'Large expense recorded: ${expense.amount} on {expense.date_purchase.strftime("%Y-%m-%d")}'
        create_notification(expense.user_id, message, 'large_expense')

def handle_new_expense(expense):
    check_for_large_expense(expense)

def create_recurring_expenses():
    with app.app_context():
        from app.models import Expenses, db  # Import inside the function to avoid circular imports
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta

        expenses = Expenses.query.filter(Expenses.recurrence.isnot(None)).all()
        for expense in expenses:
            if expense.recurrence == 'daily':
                next_date = expense.date_purchase + timedelta(days=1)
            elif expense.recurrence == 'weekly':
                next_date = expense.date_purchase + timedelta(weeks=1)
            elif expense.recurrence == 'monthly':
                next_date = expense.date_purchase + relativedelta(months=1)

            new_expense = Expenses(
                type_expense=expense.type_expense,
                description_expense=expense.description_expense,
                date_purchase=next_date,
                amount=expense.amount,
                user_id=expense.user_id,
                category_id=expense.category_id,
                recurrence=expense.recurrence
            )
            db.session.add(new_expense)
        db.session.commit()
