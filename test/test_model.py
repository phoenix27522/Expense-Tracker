import unittest
from app import db, create_app
from app.models import User, Expenses, Category, RecurringExpense
from app.config import TestingConfig
from sqlalchemy.exc import IntegrityError

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Test User Model
    def test_user_creation(self):
        user = User(email="testuser@example.com", password="validPassword123", username="testuser")
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(User.query.count(), 1)

    def test_user_validation(self):
        user = User(email="invalidemail", password="short", username="")
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_user_expense_relationship(self):
        user = User(email="testuser@example.com", password="validPassword123", username="testuser")
        expense = Expenses(amount=50.0, category="Food", description="Lunch", user=user)
        db.session.add(user)
        db.session.add(expense)
        db.session.commit()
        self.assertEqual(user.expenses.count(), 1)
        self.assertEqual(expense.user, user)

    def test_duplicate_user_email(self):
        user1 = User(email="duplicate@example.com", password="password1", username="user1")
        user2 = User(email="duplicate@example.com", password="password2", username="user2")
        db.session.add(user1)
        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_user_username_length(self):
        user = User(email="testuser@example.com", password="validPassword123", username="x" * 256)
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    # Test Expense Model
    def test_expense_creation(self):
        expense = Expenses(amount=50.0, category="Food", description="Lunch")
        db.session.add(expense)
        db.session.commit()
        self.assertIsNotNone(expense.id)
        self.assertEqual(Expenses.query.count(), 1)

    def test_expense_validation(self):
        expense = Expenses(amount=-10.0, category="Misc", description="Invalid expense")
        db.session.add(expense)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_expense_category_relationship(self):
        category = Category(name="Food")
        expense = Expenses(amount=50.0, category=category, description="Lunch")
        db.session.add(category)
        db.session.add(expense)
        db.session.commit()
        self.assertEqual(expense.category.name, "Food")

    def test_expense_unique_category(self):
        category = Category(name="Travel")
        expense1 = Expenses(amount=100.0, category=category, description="Trip")
        expense2 = Expenses(amount=200.0, category=category, description="Another Trip")
        db.session.add(category)
        db.session.add(expense1)
        db.session.add(expense2)
        db.session.commit()
        self.assertEqual(Expenses.query.count(), 2)

    def test_expense_amount_type(self):
        with self.assertRaises(TypeError):  # Expecting a TypeError due to invalid amount type
            expense = Expenses(amount="not_a_number", category="Food", description="Invalid amount")
            db.session.add(expense)
            db.session.commit()

    # Test Category Model
    def test_category_creation(self):
        category = Category(name="Food")
        db.session.add(category)
        db.session.commit()
        self.assertIsNotNone(category.id)
        self.assertEqual(Category.query.count(), 1)

    def test_duplicate_category_name(self):
        category1 = Category(name="Travel")
        category2 = Category(name="Travel")
        db.session.add(category1)
        db.session.add(category2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_category_expense_relationship(self):
        category = Category(name="Entertainment")
        expense = Expenses(amount=100.0, category=category, description="Concert")
        db.session.add(category)
        db.session.add(expense)
        db.session.commit()
        self.assertEqual(category.expenses.count(), 1)
        self.assertEqual(expense.category.name, "Entertainment")

    def test_category_name_length(self):
        category = Category(name="x" * 256)
        db.session.add(category)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_category_special_characters(self):
        category = Category(name="Gifts & Charity")
        db.session.add(category)
        db.session.commit()
        self.assertEqual(Category.query.count(), 1)

    # Test RecurringExpense Model
    def test_recurring_expense_creation(self):
        recurring_expense = RecurringExpense(amount=100.0, category="Subscription", description="Monthly magazine", recurrence="monthly")
        db.session.add(recurring_expense)
        db.session.commit()
        self.assertIsNotNone(recurring_expense.id)
        self.assertEqual(RecurringExpense.query.count(), 1)

    def test_recurring_expense_validation(self):
        recurring_expense = RecurringExpense(amount=0.0, category="Subscription", description="Zero amount", recurrence="monthly")
        db.session.add(recurring_expense)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_recurring_expense_date_validation(self):
        recurring_expense = RecurringExpense(amount=100.0, category="Subscription", description="Past start date", recurrence="monthly", start_date="2020-01-01")
        db.session.add(recurring_expense)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_recurring_expense_end_date_before_start_date(self):
        recurring_expense = RecurringExpense(amount=100.0, category="Subscription", description="End date before start date", recurrence="monthly", start_date="2024-01-01", end_date="2023-12-31")
        db.session.add(recurring_expense)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_recurring_expense_recurring_field_validation(self):
        recurring_expense = RecurringExpense(amount=100.0, category="Subscription", description="Invalid recurrence", recurrence="yearly")
        db.session.add(recurring_expense)
        with self.assertRaises(IntegrityError):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
