# Expense-Tracker

Here's a detailed documentation of the API endpoints along with usage examples for your Flask application.

### **API Documentation**

---

#### **1. Registration Endpoint**

- **URL**: `/register`
- **Method**: `POST`
- **Description**: Register a new user in the system.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  
- **Body** (JSON):
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123"
  }
  ```

**Response:**

- **Success**:
  - **Status Code**: `201 Created`
  - **Body**:
    ```json
    {
      "message": "User registered successfully"
    }
    ```

- **Error**:
  - **Status Code**: `400 Bad Request`
  - **Possible Errors**:
    - Missing fields:
      ```json
      {
        "message": "Missing required fields"
      }
      ```
    - Invalid email format:
      ```json
      {
        "message": "Invalid email format"
      }
      ```
    - User already exists:
      ```json
      {
        "message": "User already exists"
      }
      ```

**Usage Example (cURL)**:

```bash
curl -X POST http://localhost:5000/register \
-H "Content-Type: application/json" \
-d '{"username": "john_doe", "email": "john@example.com", "password": "securePassword123"}'
```

---

#### **2. Login Endpoint**

- **URL**: `/login`
- **Method**: `POST`
- **Description**: Authenticate a user and provide a JWT token.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  
- **Body** (JSON):
  ```json
  {
    "email": "john@example.com",
    "password": "securePassword123"
  }
  ```

**Response:**

- **Success**:
  - **Status Code**: `200 OK`
  - **Body**:
    ```json
    {
      "access_token": "your_jwt_token_here"
    }
    ```

- **Error**:
  - **Status Code**: `400 Bad Request`
  - **Possible Errors**:
    - Missing fields:
      ```json
      {
        "message": "Missing required fields"
      }
      ```
  - **Status Code**: `401 Unauthorized`
  - **Error**:
    - Invalid credentials:
      ```json
      {
        "message": "Invalid email or password"
      }
      ```

**Usage Example (cURL)**:

```bash
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{"email": "john@example.com", "password": "securePassword123"}'
```

---

#### **3. Logout Endpoint**

- **URL**: `/logout`
- **Method**: `POST`
- **Description**: Invalidate the JWT token for the current user.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer your_jwt_token_here`
  
- **Body**: None

**Response:**

- **Success**:
  - **Status Code**: `200 OK`
  - **Body**:
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

**Usage Example (cURL)**:

```bash
curl -X POST http://localhost:5000/logout \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_jwt_token_here"
```

---

#### **4. Add Expense Endpoint**

- **URL**: `/add_expense`
- **Method**: `POST`
- **Description**: Add a new expense for the authenticated user.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer your_jwt_token_here`
  
- **Body** (JSON):
  ```json
  {
    "type_expense": "Food",
    "description_expense": "Lunch at restaurant",
    "date_purchase": "2024-08-19",
    "amount": 15.99
  }
  ```

**Response:**

- **Success**:
  - **Status Code**: `201 Created`
  - **Body**:
    ```json
    {
      "message": "Expense added successfully"
    }
    ```

- **Error**:
  - **Status Code**: `400 Bad Request`
  - **Possible Errors**:
    - Missing fields or validation errors:
      ```json
      {
        "message": "Validation failed: missing or incorrect fields"
      }
      ```

**Usage Example (cURL)**:

```bash
curl -X POST http://localhost:5000/add_expense \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_jwt_token_here" \
-d '{"type_expense": "Food", "description_expense": "Lunch at restaurant", "date_purchase": "2024-08-19", "amount": 15.99}'
```

---

#### **5. Show Expenses Endpoint**

- **URL**: `/expenses`
- **Method**: `GET`
- **Description**: Retrieve a list of expenses for a specific user.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer your_jwt_token_here`
  
- **Query Parameters**:
  - `user`: The username whose expenses are to be retrieved.
  
**Response:**

- **Success**:
  - **Status Code**: `200 OK`
  - **Body**:
    ```json
    [
      {
        "expense_id": 1,
        "type_expense": "Food",
        "description_expense": "Lunch at restaurant",
        "date_purchase": "2024-08-19",
        "amount": 15.99,
        "user_name": "john_doe"
      },
      ...
    ]
    ```

**Usage Example (cURL)**:

```bash
curl -X GET "http://localhost:5000/expenses?user=john_doe" \
-H "Authorization: Bearer your_jwt_token_here"
```

---

#### **6. Modify Expense Endpoint**

- **URL**: `/mod_expense`
- **Method**: `POST`
- **Description**: Modify an existing expense or delete it.

**Request:**

- **Headers**:
  - `Content-Type`: `application/json`
  - `Authorization`: `Bearer your_jwt_token_here`
  
- **Body** (JSON):
  ```json
  {
    "Type": "Food",
    "Description": "Lunch at a cafe",
    "Date": "2024-08-19",
    "Amount": 12.50,
    "Delete": false
  }
  ```

**Response:**

- **Success**:
  - **Status Code**: `200 OK`
  - **Body**:
    ```json
    {
      "message": "Expense modified successfully"
    }
    ```

- **Error**:
  - **Status Code**: `400 Bad Request`
  - **Possible Errors**:
    - Expense not found or validation errors:
      ```json
      {
        "message": "Expense not found or validation failed"
      }
      ```

**Usage Example (cURL)**:

```bash
curl -X POST http://localhost:5000/mod_expense \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_jwt_token_here" \
-d '{"Type": "Food", "Description": "Lunch at a cafe", "Date": "2024-08-19", "Amount": 12.50, "Delete": false}'
```
