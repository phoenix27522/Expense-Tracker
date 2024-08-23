import unittest
from app import db, bcrypt, create_app
from app.models import User, Category, Expenses, RecurringExpense, Notification
from sqlalchemy.exc import IntegrityError
from app.config import TestingConfig
from datetime import datetime, timedelta

class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user creation with valid data."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword") 
        db.session.add(user)
        db.session.commit()

        fetched_user = User.query.filter_by(user_name="testuser").first()
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.email, "test@example.com")

    def test_duplicate_email_and_user_name(self):
        """Test that duplicate email and username combination raises an IntegrityError."""
        user1 = User(user_name="testuser", email="test@example.com")
        user1.set_password("securepassword")
        db.session.add(user1)
        db.session.commit()

        user2 = User(user_name="testuser", email="test@example.com")
        user2.set_password("anotherpassword")

        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_unique_username(self):
        """Test that creating two users with the same username but different emails raises an IntegrityError."""
        user1 = User(user_name="testuser", email="test1@example.com")
        user1.set_password("securepassword")
        db.session.add(user1)
        db.session.commit()

        user2 = User(user_name="testuser", email="test2@example.com")
        user2.set_password("anotherpassword")

        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_unique_email(self):
        """Test that creating two users with the same email but different usernames raises an IntegrityError."""
        user1 = User(user_name="testuser1", email="test@example.com")
        user1.set_password("securepassword")
        db.session.add(user1)
        db.session.commit()

        user2 = User(user_name="testuser2", email="test@example.com")
        user2.set_password("anotherpassword")

        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_password_hashing(self):
        """Test that the password is hashed and stored correctly."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        fetched_user = User.query.filter_by(user_name="testuser").first()
        self.assertIsNotNone(fetched_user.password_hash)
        self.assertNotEqual(fetched_user.password_hash, "securepassword")
        self.assertTrue(bcrypt.check_password_hash(fetched_user.password_hash, "securepassword"))

    def test_password_length_validation(self):
        """Test that setting a password with fewer than 8 characters raises a ValueError."""
        user = User(user_name="testuser", email="test@example.com")
        with self.assertRaises(ValueError):
            user.set_password("short")

    def test_invalid_email_format(self):
        """Test that setting an invalid email format raises a ValueError."""
        user = User(user_name="testuser", email="invalid-email")
        with self.assertRaises(ValueError):
            user.set_email("invalid-email")

    def test_invalid_username_format(self):
        """Test that setting a username with special characters raises a ValueError."""
        user = User(user_name="invalid_user!@", email="test@example.com")
        with self.assertRaises(ValueError):
            user.set_username("invalid_user!@")
  
class CategoryModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_creation(self):
        """Test category creation with valid data."""
        category = Category(name="Food")
        db.session.add(category)
        db.session.commit()

        fetched_category = Category.query.filter_by(name="Food").first()
        self.assertIsNotNone(fetched_category)
        self.assertEqual(fetched_category.name, "Food")

    def test_duplicate_category_name(self):
        """Test that creating two categories with the same name raises an IntegrityError."""
        category1 = Category(name="Food")
        db.session.add(category1)
        db.session.commit()

        category2 = Category(name="Food")
        db.session.add(category2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_category_name_length(self):
        """Test that setting a category name longer than 50 characters raises a ValueError."""
        category = Category(name="A" * 51)
        with self.assertRaises(ValueError):
            category.set_name("A" * 51)

class ExpensesModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_expense_creation(self):
        """Test expense creation with valid data."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Food")
        db.session.add(category)
        db.session.commit()

        expense = Expenses(amount=20.0, description="Groceries", date=datetime.utcnow(), user_id=user.id, category_id=category.id)
        db.session.add(expense)
        db.session.commit()

        fetched_expense = Expenses.query.filter_by(description="Groceries").first()
        self.assertIsNotNone(fetched_expense)
        self.assertEqual(fetched_expense.amount, 20.0)
        self.assertEqual(fetched_expense.description, "Groceries")

    def test_invalid_date(self):
        """Test that setting an invalid date raises a ValueError."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Food")
        db.session.add(category)
        db.session.commit()

        with self.assertRaises(ValueError):
            expense = Expenses(amount=20.0, description="Groceries", date="invalid-date", user_id=user.id, category_id=category.id)

    def test_negative_amount(self):
        """Test that setting a negative amount raises a ValueError."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Food")
        db.session.add(category)
        db.session.commit()

        with self.assertRaises(ValueError):
            expense = Expenses(amount=-20.0, description="Groceries", date=datetime.utcnow(), user_id=user.id, category_id=category.id)

class RecurringExpenseModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_recurring_expense_creation(self):
        """Test recurring expense creation with valid data."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Subscriptions")
        db.session.add(category)
        db.session.commit()

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        recurring_expense = RecurringExpense(amount=50.0, type_expense="Subscription", description_expense="Netflix", recurrence="monthly", start_date=start_date, end_date=end_date, user_id=user.id, category_id=category.id)
        db.session.add(recurring_expense)
        db.session.commit()

        fetched_recurring_expense = RecurringExpense.query.filter_by(description_expense="Netflix").first()
        self.assertIsNotNone(fetched_recurring_expense)
        self.assertEqual(fetched_recurring_expense.amount, 50.0)
        self.assertEqual(fetched_recurring_expense.type_expense, "Subscription")
        self.assertEqual(fetched_recurring_expense.recurrence, "monthly")

    def test_invalid_recurrence_format(self):
        """Test that setting an invalid recurrence format raises a ValueError."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Subscriptions")
        db.session.add(category)
        db.session.commit()

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)

        with self.assertRaises(ValueError):
            recurring_expense = RecurringExpense(amount=50.0, type_expense="Subscription", description_expense="Netflix", recurrence="invalid-recurrence", start_date=start_date, end_date=end_date, user_id=user.id, category_id=category.id)

    def test_end_date_before_start_date(self):
        """Test that setting an end date before the start date raises a ValueError."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        category = Category(name="Subscriptions")
        db.session.add(category)
        db.session.commit()

        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=30)

        with self.assertRaises(ValueError):
            recurring_expense = RecurringExpense(amount=50.0, type_expense="Subscription", description_expense="Netflix", recurrence="monthly", start_date=start_date, end_date=end_date, user_id=user.id, category_id=category.id)

class NotificationModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_notification_creation(self):
        """Test notification creation with valid data."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        notification = Notification(user_id=user.id, message="Expense threshold exceeded", type="warning")
        db.session.add(notification)
        db.session.commit()

        fetched_notification = Notification.query.filter_by(message="Expense threshold exceeded").first()
        self.assertIsNotNone(fetched_notification)
        self.assertEqual(fetched_notification.message, "Expense threshold exceeded")
        self.assertEqual(fetched_notification.type, "warning")

    def test_notification_is_read_flag(self):
        """Test that the is_read flag is correctly set."""
        user = User(user_name="testuser", email="test@example.com")
        user.set_password("securepassword")
        db.session.add(user)
        db.session.commit()

        notification = Notification(user_id=user.id, message="Expense threshold exceeded", type="warning", is_read=True)
        db.session.add(notification)
        db.session.commit()

        fetched_notification = Notification.query.filter_by(message="Expense threshold exceeded").first()
        self.assertTrue(fetched_notification.is_read)

        # Also check the default value of is_read when not explicitly set
        notification_unread = Notification(user_id=user.id, message="New expense added", type="info")
        db.session.add(notification_unread)
        db.session.commit()

        fetched_notification_unread = Notification.query.filter_by(message="New expense added").first()
        self.assertFalse(fetched_notification_unread.is_read)

if __name__ == "__main__":
    unittest.main()
