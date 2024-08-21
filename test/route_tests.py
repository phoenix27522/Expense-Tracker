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


if __name__ == '__main__':
    unittest.main()
