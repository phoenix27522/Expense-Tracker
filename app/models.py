from app import db, bcrypt
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import re

def validate_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.match(regex, email):
        raise ValueError("Invalid email format")

def validate_username(username):
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        raise ValueError("Username can only contain alphanumeric characters and underscores")

def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

def validate_amount(amount):
    if amount < 0:
        raise ValueError("Amount cannot be negative")

def validate_date(date):
    if not isinstance(date, datetime):
        raise ValueError("Date must be a datetime object")

def validate_recurrence(recurrence):
    if not re.match(r'^[A-Za-z0-9]+$', recurrence):
        raise ValueError("Invalid recurrence format")

class User(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    user_name = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expenses = relationship('Expenses', back_populates='user')
    recurring_expenses = relationship('RecurringExpense', back_populates='user')

    def set_password(self, password):
        validate_password(password)
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def set_email(self, email):
        validate_email(email)
        self.email = email

    def set_username(self, username):
        validate_username(username)
        self.user_name = username

class Expenses(db.Model):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses_list')

    def set_amount(self, amount):
        validate_amount(amount)
        self.amount = amount

    def set_date(self, date):
        validate_date(date)
        self.date = date

class Category(db.Model):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # Relationships
    expenses_list = relationship('Expenses', back_populates='category')
    recurring_expenses_list = relationship('RecurringExpense', back_populates='category')

    def set_name(self, name):
        if len(name) > 50:
            raise ValueError("Category name is too long")
        self.name = name

class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expense'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    type_expense = Column(String(255), nullable=False)
    description_expense = Column(String(255), nullable=False)
    recurrence = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='recurring_expenses')
    category = relationship('Category', back_populates='recurring_expenses_list')

    def set_recurrence(self, recurrence):
        validate_recurrence(recurrence)
        self.recurrence = recurrence

    def set_dates(self, start_date, end_date):
        validate_date(start_date)
        validate_date(end_date)
        if end_date < start_date:
            raise ValueError("End date cannot be before start date")
        self.start_date = start_date
        self.end_date = end_date

class Notification(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    def __repr__(self):
        return f'<Notification {self.message}>'
