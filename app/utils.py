from app.models import Notification, User, db
from werkzeug.security import check_password_hash

def verify_user_credentials(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

def create_notification(user_id, message, type):
    notification = Notification(user_id=user_id, message=message, type=type)
    db.session.add(notification)
    db.session.commit()

def check_for_large_expense(expense):
    # Define the threshold for a "large" expense
    threshold = 1000  # Example threshold
    if expense.amount >= threshold:
        message = f'Large expense recorded: ${expense.amount} on {expense.date_purchase.strftime("%Y-%m-%d")}'
        create_notification(expense.user_name, message, 'large_expense')

# Call this function whenever a new expense is created
def handle_new_expense(expense):
    check_for_large_expense(expense)
    # Add other checks if necessary
