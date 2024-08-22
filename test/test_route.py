import unittest
import requests

class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/register"
    
    def test_valid_registration(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123",
            "username": "testuser"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_email_format(self):
        response = requests.post(self.base_url, json={
            "email": "invalidemail",
            "password": "validPassword123",
            "username": "testuser"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_short_password(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "short",
            "username": "testuser"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_duplicate_email(self):
        response = requests.post(self.base_url, json={
            "email": "existinguser@example.com",
            "password": "validPassword123",
            "username": "testuser"
        })
        self.assertEqual(response.status_code, 409)
    
    def test_empty_fields(self):
        response = requests.post(self.base_url, json={
            "email": "",
            "password": "validPassword123",
            "username": ""
        })
        self.assertEqual(response.status_code, 400)

    def test_sql_injection_attempt(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123",
            "username": "'; DROP TABLE users; --"
        })
        self.assertEqual(response.status_code, 400)

    def test_max_length_exceeded(self):
        response = requests.post(self.base_url, json={
            "email": "a" * 256 + "@example.com",
            "password": "validPassword123",
            "username": "a" * 256
        })
        self.assertEqual(response.status_code, 400)

    def test_uncommon_characters(self):
        response = requests.post(self.base_url, json={
            "email": "test+special@example.com",
            "password": "validPassword123",
            "username": "test_user@#$"
        })
        self.assertEqual(response.status_code, 201)

    # New test cases

    def test_whitespace_handling(self):
        response = requests.post(self.base_url, json={
            "email": "   testuser@example.com   ",
            "password": "   validPassword123   ",
            "username": "   testuser   "
        })
        self.assertEqual(response.status_code, 201)

    def test_case_sensitivity_in_email(self):
        response = requests.post(self.base_url, json={
            "email": "TestUser@Example.com",
            "password": "validPassword123",
            "username": "testuser"
        })
        self.assertEqual(response.status_code, 201)

    def test_minimum_length_username_password(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "12345678",  # Assuming 8 is the minimum password length
            "username": "user"  # Assuming 4 is the minimum username length
        })
        self.assertEqual(response.status_code, 201)

    def test_empty_json_object(self):
        response = requests.post(self.base_url, json={})
        self.assertEqual(response.status_code, 400)

""" test case for the user login """
class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/login"
    
    def test_valid_login(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_password(self):
        response = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "wrongPassword"
        })
        self.assertEqual(response.status_code, 401)
    
    def test_unregistered_email(self):
        response = requests.post(self.base_url, json={
            "email": "unknown@example.com",
            "password": "validPassword123"
        })
        self.assertEqual(response.status_code, 404)
    
    def test_empty_fields(self):
        response = requests.post(self.base_url, json={
            "email": "",
            "password": ""
        })
        self.assertEqual(response.status_code, 400)

    def test_case_sensitivity(self):
        response = requests.post(self.base_url, json={
            "email": "TestUser@Example.com",
            "password": "ValidPassword123"
        })
        self.assertEqual(response.status_code, 200)
    
    def test_account_lock(self):
        for _ in range(5):
            response = requests.post(self.base_url, json={
                "email": "testuser@example.com",
                "password": "wrongPassword"
            })
        self.assertEqual(response.status_code, 423)  # Account locked
    
    def test_simultaneous_logins(self):
        response1 = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        response2 = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
    
    # New test cases

    def test_sql_injection_attempt(self):
        response = requests.post(self.base_url, json={
            "email": "' OR 1=1 --",
            "password": "anyPassword"
        })
        self.assertEqual(response.status_code, 400)

    def test_login_with_special_characters(self):
        response = requests.post(self.base_url, json={
            "email": "test+special@example.com",
            "password": "validPassword123"
        })
        self.assertEqual(response.status_code, 200)

    def test_max_length_exceeded(self):
        response = requests.post(self.base_url, json={
            "email": "a" * 256 + "@example.com",
            "password": "a" * 256
        })
        self.assertEqual(response.status_code, 400)
    
    def test_login_after_password_change(self):
        # Simulate changing the password
        response = requests.post(self.base_url.replace("/login", "/change-password"), json={
            "email": "testuser@example.com",
            "old_password": "validPassword123",
            "new_password": "newValidPassword123"
        })
        self.assertEqual(response.status_code, 200)

        # Attempt login with the old password
        response_old = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        self.assertEqual(response_old.status_code, 401)

        # Attempt login with the new password
        response_new = requests.post(self.base_url, json={
            "email": "testuser@example.com",
            "password": "newValidPassword123"
        })
        self.assertEqual(response_new.status_code, 200)

    def test_login_with_whitespace(self):
        response = requests.post(self.base_url, json={
            "email": "   testuser@example.com   ",
            "password": "   validPassword123   "
        })
        self.assertEqual(response.status_code, 200)

""" test for CRUDE of the expence"""
class TestExpenseManagement(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/expenses"
    
    def test_add_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Food",
            "description": "Lunch"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_edit_expense(self):
        response = requests.put(self.base_url + "/1", json={
            "amount": 75.0,
            "category": "Dining",
            "description": "Dinner"
        })
        self.assertEqual(response.status_code, 200)
    
    def test_delete_expense(self):
        response = requests.delete(self.base_url + "/1")
        self.assertEqual(response.status_code, 204)
    
    def test_view_expense(self):
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 200)

    # New Test Cases

    def test_negative_amount(self):
        response = requests.post(self.base_url, json={
            "amount": -10.0,
            "category": "Misc",
            "description": "Negative test"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_future_date(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "Savings",
            "description": "Future expense",
            "date": "2100-01-01"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_large_amount(self):
        response = requests.post(self.base_url, json={
            "amount": 1e6,
            "category": "Investment",
            "description": "Large expense"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_empty_fields(self):
        response = requests.post(self.base_url, json={
            "amount": "",
            "category": "",
            "description": ""
        })
        self.assertEqual(response.status_code, 400)
    
    # Additional Edge Cases

    def test_max_length_exceeded(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "a" * 256,
            "description": "a" * 256
        })
        self.assertEqual(response.status_code, 400)
    
    def test_duplicate_expense_entry(self):
        # Add an expense first
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Groceries",
            "description": "Milk and bread"
        })
        self.assertEqual(response.status_code, 201)

        # Attempt to add the same expense again
        response_duplicate = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Groceries",
            "description": "Milk and bread"
        })
        self.assertEqual(response_duplicate.status_code, 409)

    def test_invalid_date_format(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "Utilities",
            "description": "Electric bill",
            "date": "invalid-date"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_edit_nonexistent_expense(self):
        response = requests.put(self.base_url + "/9999", json={
            "amount": 75.0,
            "category": "Dining",
            "description": "Updated dinner"
        })
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_expense(self):
        response = requests.delete(self.base_url + "/9999")
        self.assertEqual(response.status_code, 404)

    def test_expense_with_special_characters(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "Miscellaneous",
            "description": "Expense with special characters @#$%^&*()"
        })
        self.assertEqual(response.status_code, 201)

    def test_expense_with_whitespace(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "   Food   ",
            "description": "   Pizza   "
        })
        self.assertEqual(response.status_code, 201)

""" test for the expence catograzation"""
class TestExpenseCategorization(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/categories"
    
    def test_valid_categorization(self):
        response = requests.post(self.base_url, json={
            "name": "Entertainment"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_category(self):
        response = requests.post(self.base_url, json={
            "name": ""
        })
        self.assertEqual(response.status_code, 400)
    
    def test_empty_category(self):
        response = requests.post(self.base_url, json={
            "name": ""
        })
        self.assertEqual(response.status_code, 400)
    
    def test_duplicate_category_names(self):
        response1 = requests.post(self.base_url, json={
            "name": "Travel"
        })
        self.assertEqual(response1.status_code, 201)

        response2 = requests.post(self.base_url, json={
            "name": "travel"
        })
        self.assertEqual(response2.status_code, 409)
    
    def test_special_characters_in_category(self):
        response = requests.post(self.base_url, json={
            "name": "Gifts & Charity"
        })
        self.assertEqual(response.status_code, 201)

    # Additional Edge Cases

    def test_max_length_exceeded(self):
        response = requests.post(self.base_url, json={
            "name": "a" * 256
        })
        self.assertEqual(response.status_code, 400)
    
    def test_category_with_whitespace(self):
        response = requests.post(self.base_url, json={
            "name": "   Food   "
        })
        self.assertEqual(response.status_code, 201)

    def test_category_with_numbers(self):
        response = requests.post(self.base_url, json={
            "name": "Groceries 2024"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_category_with_only_numbers(self):
        response = requests.post(self.base_url, json={
            "name": "12345"
        })
        self.assertEqual(response.status_code, 400)

    def test_category_with_symbols(self):
        response = requests.post(self.base_url, json={
            "name": "Utilities @ Home"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_update_existing_category(self):
        # Creating a category
        response_create = requests.post(self.base_url, json={
            "name": "Health"
        })
        self.assertEqual(response_create.status_code, 201)
        
        # Updating the category
        response_update = requests.put(self.base_url + "/1", json={
            "name": "Healthcare & Wellness"
        })
        self.assertEqual(response_update.status_code, 200)

    def test_delete_existing_category(self):
        # Creating a category
        response_create = requests.post(self.base_url, json={
            "name": "Subscriptions"
        })
        self.assertEqual(response_create.status_code, 201)
        
        # Deleting the category
        response_delete = requests.delete(self.base_url + "/1")
        self.assertEqual(response_delete.status_code, 204)

    def test_delete_nonexistent_category(self):
        response = requests.delete(self.base_url + "/9999")
        self.assertEqual(response.status_code, 404)

"""Test RecurringExpenses EdgeCases"""
class TestRecurringExpensesEdgeCases(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/recurring_expenses"
    
    def test_add_recurring_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 100.0,
            "category": "Subscription",
            "description": "Monthly magazine subscription",
            "recurrence": "monthly"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_edit_recurring_expense(self):
        response = requests.put(self.base_url + "/1", json={
            "amount": 120.0,
            "category": "Subscription",
            "description": "Updated subscription",
            "recurrence": "monthly"
        })
        self.assertEqual(response.status_code, 200)
    
    def test_delete_recurring_expense(self):
        response = requests.delete(self.base_url + "/1")
        self.assertEqual(response.status_code, 204)
    
    def test_view_recurring_expenses(self):
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_recurrence_frequency(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Invalid recurrence test",
            "recurrence": "weekly"  # Assuming weekly is not allowed
        })
        self.assertEqual(response.status_code, 400)
    
    def test_conflicting_recurring_expenses(self):
        response1 = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Monthly magazine",
            "recurrence": "monthly"
        })
        self.assertEqual(response1.status_code, 201)
        response2 = requests.post(self.base_url, json={
            "amount": 70.0,
            "category": "Subscription",
            "description": "Conflicting monthly magazine",
            "recurrence": "monthly"
        })
        self.assertEqual(response2.status_code, 409)
    
    def test_missing_recurrence_field(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Missing recurrence field"
        })
        self.assertEqual(response.status_code, 400)

    def test_zero_amount_recurring_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 0.0,
            "category": "Subscription",
            "description": "Zero amount test",
            "recurrence": "monthly"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_past_start_date_recurring_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Past start date test",
            "recurrence": "monthly",
            "start_date": "2020-01-01"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_recurring_expense_end_date_before_start_date(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "End date before start date",
            "recurrence": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2023-12-31"
        })
        self.assertEqual(response.status_code, 400)

    # Additional Edge Cases

    def test_invalid_date_format(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Invalid date format",
            "recurrence": "monthly",
            "start_date": "01-01-2024"  # Incorrect date format
        })
        self.assertEqual(response.status_code, 400)
    
    def test_missing_amount_field(self):
        response = requests.post(self.base_url, json={
            "category": "Subscription",
            "description": "Missing amount field",
            "recurrence": "monthly"
        })
        self.assertEqual(response.status_code, 400)

    def test_large_amount_recurring_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 1e6,
            "category": "Subscription",
            "description": "Large amount test",
            "recurrence": "monthly"
        })
        self.assertEqual(response.status_code, 201)

    def test_future_end_date(self):
        response = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Future end date test",
            "recurrence": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2100-01-01"
        })
        self.assertEqual(response.status_code, 201)

    def test_redundant_recurring_expense_creation(self):
        response1 = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Redundant creation test",
            "recurrence": "monthly"
        })
        self.assertEqual(response1.status_code, 201)
        
        response2 = requests.post(self.base_url, json={
            "amount": 50.0,
            "category": "Subscription",
            "description": "Redundant creation test",
            "recurrence": "monthly"
        })
        self.assertEqual(response2.status_code, 409)

"""Test Filtering And Sorting Expenses"""
class TestFilteringAndSortingExpenses(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/expenses"

    def test_filter_by_category(self):
        response = requests.get(self.base_url + "?category=Food")
        self.assertEqual(response.status_code, 200)
        for expense in response.json():
            self.assertEqual(expense['category'], 'Food')
    
    def test_filter_by_date_range(self):
        response = requests.get(self.base_url + "?start_date=2024-01-01&end_date=2024-01-31")
        self.assertEqual(response.status_code, 200)
        for expense in response.json():
            self.assertTrue("2024-01-01" <= expense['date'] <= "2024-01-31")
    
    def test_sort_by_amount_ascending(self):
        response = requests.get(self.base_url + "?sort_by=amount&order=asc")
        self.assertEqual(response.status_code, 200)
        expenses = response.json()
        amounts = [expense['amount'] for expense in expenses]
        self.assertEqual(amounts, sorted(amounts))
    
    def test_sort_by_date_descending(self):
        response = requests.get(self.base_url + "?sort_by=date&order=desc")
        self.assertEqual(response.status_code, 200)
        expenses = response.json()
        dates = [expense['date'] for expense in expenses]
        self.assertEqual(dates, sorted(dates, reverse=True))
    
    def test_combined_filtering_and_sorting(self):
        response = requests.get(self.base_url + "?category=Travel&start_date=2024-06-01&end_date=2024-06-30&sort_by=amount&order=asc")
        self.assertEqual(response.status_code, 200)
        expenses = response.json()
        amounts = [expense['amount'] for expense in expenses]
        self.assertEqual(amounts, sorted(amounts))
        for expense in expenses:
            self.assertEqual(expense['category'], 'Travel')
            self.assertTrue("2024-06-01" <= expense['date'] <= "2024-06-30")

    # Additional Edge Cases

    def test_filter_with_no_results(self):
        response = requests.get(self.base_url + "?category=NonExistentCategory")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
    
    def test_invalid_date_format(self):
        response = requests.get(self.base_url + "?start_date=01-01-2024&end_date=31-01-2024")
        self.assertEqual(response.status_code, 400)

    def test_invalid_sort_field(self):
        response = requests.get(self.base_url + "?sort_by=invalid_field&order=asc")
        self.assertEqual(response.status_code, 400)

    def test_invalid_order(self):
        response = requests.get(self.base_url + "?sort_by=amount&order=invalid_order")
        self.assertEqual(response.status_code, 400)
    
    def test_missing_sort_by_parameter(self):
        response = requests.get(self.base_url + "?sort_by=&order=asc")
        self.assertEqual(response.status_code, 400)
    
    def test_combined_filtering_no_results(self):
        response = requests.get(self.base_url + "?category=NonExistentCategory&start_date=2024-06-01&end_date=2024-06-30&sort_by=amount&order=asc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)


"""Test Notifications For Large Expenses"""
class TestNotificationsForLargeExpenses(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000/expenses"
        self.notifications_url = "http://localhost:5000/notifications"
    
    def test_notification_trigger_for_large_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 5000.0,
            "category": "Electronics",
            "description": "New laptop"
        })
        self.assertEqual(response.status_code, 201)
        # Check notifications
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        self.assertTrue(any("large expense" in notification['message'].lower() for notification in notifications))
    
    def test_no_notification_for_small_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 10.0,
            "category": "Snacks",
            "description": "Chips"
        })
        self.assertEqual(response.status_code, 201)
        # Check notifications
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        self.assertFalse(any("large expense" in notification['message'].lower() for notification in notifications))

    def test_notification_message_content(self):
        response = requests.post(self.base_url, json={
            "amount": 7500.0,
            "category": "Furniture",
            "description": "New sofa set"
        })
        self.assertEqual(response.status_code, 201)
        # Check notifications
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        relevant_notifications = [notification for notification in notifications if "large expense" in notification['message'].lower()]
        self.assertTrue(any("7500.0" in notification['message'] for notification in relevant_notifications))
        self.assertTrue(any("Furniture" in notification['message'] for notification in relevant_notifications))

    def test_notification_not_repeated(self):
        response = requests.post(self.base_url, json={
            "amount": 10000.0,
            "category": "Travel",
            "description": "Vacation"
        })
        self.assertEqual(response.status_code, 201)
        notification_response1 = requests.get(self.notifications_url)
        self.assertEqual(notification_response1.status_code, 200)
        notifications1 = notification_response1.json()

        response = requests.post(self.base_url, json={
            "amount": 10000.0,
            "category": "Travel",
            "description": "Another Vacation"
        })
        self.assertEqual(response.status_code, 201)
        notification_response2 = requests.get(self.notifications_url)
        self.assertEqual(notification_response2.status_code, 200)
        notifications2 = notification_response2.json()

        self.assertEqual(len(notifications1), len(notifications2))

    # Additional Edge Cases

    def test_notification_for_zero_amount_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 0.0,
            "category": "Misc",
            "description": "Zero amount test"
        })
        self.assertEqual(response.status_code, 201)
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        self.assertFalse(any("large expense" in notification['message'].lower() for notification in notifications))

    def test_multiple_large_expenses(self):
        response1 = requests.post(self.base_url, json={
            "amount": 6000.0,
            "category": "Electronics",
            "description": "TV"
        })
        self.assertEqual(response1.status_code, 201)
        response2 = requests.post(self.base_url, json={
            "amount": 7000.0,
            "category": "Furniture",
            "description": "Table"
        })
        self.assertEqual(response2.status_code, 201)
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        self.assertTrue(any("large expense" in notification['message'].lower() for notification in notifications))
        self.assertEqual(len([n for n in notifications if "large expense" in n['message'].lower()]), 2)

    def test_notification_for_edge_case_expense(self):
        response = requests.post(self.base_url, json={
            "amount": 99999.99,  # Assuming this is a special edge case
            "category": "Luxury",
            "description": "Exotic vacation"
        })
        self.assertEqual(response.status_code, 201)
        notification_response = requests.get(self.notifications_url)
        self.assertEqual(notification_response.status_code, 200)
        notifications = notification_response.json()
        self.assertTrue(any("large expense" in notification['message'].lower() for notification in notifications))


if __name__ == '__main__':
    unittest.main()
