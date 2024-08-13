from app.models import User
from werkzeug.security import check_password_hash

def verify_user_credentials(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
