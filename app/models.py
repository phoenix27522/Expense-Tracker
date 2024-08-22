from app import db, bcrypt
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Expenses(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    type_expense = db.Column(db.String(120), nullable=False)
    description_expense = db.Column(db.String(120), nullable=False)
    date_purchase = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    recurrence = db.Column(db.String(20), nullable=True)
    recurrence_end_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('expenses', lazy=True))
    category = db.relationship('Category', backref=db.backref('expenses_list', lazy=True))

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type_expense = db.Column(db.String(120), nullable=False)
    description_expense = db.Column(db.String(255), nullable=False)
    recurrence = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    user = db.relationship('User', backref='recurring_expenses')
    category = db.relationship('Category', backref='recurring_expenses_list')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Updated backref name from 'expenses' to 'expenses_list' to avoid conflict
    expenses_list = db.relationship('Expenses', backref='category', lazy=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Notification {self.message}>'
