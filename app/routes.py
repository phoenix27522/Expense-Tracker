import bcrypt
from flask import Flask, render_template, request, url_for, redirect, jsonify, Blueprint
from app.models import Category, User, Expenses  # Correct model names
from app.forms import AddUser, AddExpense, ModExpense
from datetime import date
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app.utils import verify_user_credentials
from app import blacklist, db, jwt
import re

main = Blueprint('main', __name__)

@main.route('/')
def home(): 
    count_users = User.query.count()
    if count_users==0: 
        return render_template("home.html")
    else: 
        users = User.query.all() 
        return render_template("home.html", users=users)
    
@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('user_name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    user_name = data['user_name']
    email = data['email']
    password = data['password']

    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.match(email_regex, email):
        return jsonify({'message': 'Invalid email format'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password too short, must be at least 6 characters'}), 400

    existing_user = User.query.filter((User.user_name == user_name) | (User.email == email)).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    user = User(
        user_name=user_name,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    email = data['email']
    password = data['password']

    user = verify_user_credentials(email, password)
    if user is None:
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@main.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Successfully logged out'}), 200

@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Welcome, user {current_user}'}), 200

@main.route('/add_user', methods=['GET', 'POST'])
def adding_new_users():

    form = AddUser (request.form)

    if request.method == 'GET':
        return render_template("add_user.html", form=form)
    else:
        try: 
            new_user = User(name=request.values.get("Name"), email=request.values.get("Email_address"))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home"))

        except Exception as e:
            error= "" 
            if "users.email_address" in str(e): 
                    error = "This email is already in use, please use a different email"
            else: 
                    error = "This name is already in use, please use a different name"
            return render_template('add_user.html', form=form, error_db_insert=error)
        

@main.route('/expenses')
def show_expenses():
    name_user = request.values.get("user")
    if name_user is None:
        return redirect(url_for("home"))
    else:
        expenses_user = db.session.query(Expenses).join(User).filter(User.name == name_user).all()
        if not expenses_user:
            return render_template("expenses.html", name_user=name_user)
        else:
            total_amount = sum([expense.amount for expense in expenses_user])
            return render_template("expenses.html", expenses=expenses_user, name_user=name_user, total=round(total_amount, 2))

@main.route('/add_expense', methods=['GET', 'POST'] )
def adding_new_expenses():
    
    name_user = request.values.get("user")
    
    if name_user ==None: 
        return redirect (url_for("home"))
    else: 
        form = AddExpense(request.form)

    categories = Category.query.all()
    if request.method == 'GET':
        return render_template("add_expense.html", form=form, categories=categories)
    else:
        if form.validate():
            category_id = request.values.get("Category")
            new_expense = Expenses(
                type_expense=request.values.get("Type"),
                description_expense=request.values.get("Description"),
                date_purchase=request.values.get("Date"),
                amount=request.values.get("Amount"),
                user_name=name_user,
                category_id=category_id
            )
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for("show_expenses", user=name_user))
        else:
            return render_template("add_expense.html", form=form, categories=categories)

@main.route('/mod_expense', methods=['GET', 'POST'] )
def modifying_expenses():   
    name_user = request.values.get("user")
    expense_id = request.values.get ("id")

    if name_user == None or expense_id == None: 
        return redirect (url_for("home"))
    else: 

        query = db.session.query (Expenses).filter (Expenses.expense_id == expense_id)

        for data in query: 
            type_expense = data.type_expense
            description_expense = data.description_expense
            date_purchase = data.date_purchase
            amount = data.amount

        if request.method == 'GET':
            form = ModExpense (data= {"Type" : type_expense,
                                    "Description": description_expense,
                                    "Date": date (int(date_purchase[:4]), int(date_purchase[5:7]), int(date_purchase[8:])),
                                    "Amount":amount })
            return render_template("mod_expense.html", form=form)
        else:

            form = ModExpense (request.form)

            if request.form.get ("Delete"): 

                query3 = Expenses.query.filter (Expenses.expense_id == expense_id).first() 
                db.session.delete (query3)
                db.session.commit() 
                return redirect(url_for("show_expenses", user = name_user))

            if form.validate(): 
            
                if request.form.get ("Save_changes"): 
                    query2 = Expenses.query.filter (Expenses.expense_id == expense_id).all()
                    for element in query2: 
                        element.type_expense = form.Type.data
                        element.description_expense = form.Description.data 
                        element.date_purchase = form.Date.data
                        element.amount = form.Amount.data 
                    db.session.commit() 
                
                    return redirect(url_for("show_expenses", user = name_user))
            else: 
                return render_template("mod_expense.html", form=form)

@main.route('/filter_expenses', methods=['GET'])
@jwt_required()
def filter_expenses():
    user_name = get_jwt_identity()

    # Retrieve query parameters
    type_expense = request.args.get('type_expense')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'date_purchase')  # Default sorting by date_purchase
    order = request.args.get('order', 'asc')

    # Build the query
    query = Expenses.query.filter_by(user_name=user_name)

    if type_expense:
        query = query.filter(Expenses.type_expense == type_expense)

    if min_amount is not None:
        query = query.filter(Expenses.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expenses.amount <= max_amount)

    if start_date:
        query = query.filter(Expenses.date_purchase >= start_date)

    if end_date:
        query = query.filter(Expenses.date_purchase <= end_date)

    if order == 'asc':
        query = query.order_by(getattr(Expenses, sort_by).asc())
    else:
        query = query.order_by(getattr(Expenses, sort_by).desc())

    expenses = query.all()

    # Serialize the data
    result = []
    for expense in expenses:
        expense_data = {
            'id': expense.expense_id,
            'type_expense': expense.type_expense,
            'description_expense': expense.description_expense,
            'date_purchase': expense.date_purchase.strftime('%Y-%m-%d'),
            'amount': expense.amount,
            'user_name': expense.user_name,
        }
        result.append(expense_data)

    return jsonify(result), 200

@main.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()

        # Retrieve the user from the database
        user = User.query.get(user_id)

        # Check if the user exists
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Return the user profile details
        return jsonify({
            'user_name': user.user_name,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        # Log the error for debugging (you might want to log to a file instead)
        print(f"Error in view_profile: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@main.route('/profile', methods=['PUT'])
@jwt_required()
def edit_profile():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()

        # Retrieve the user from the database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get the data from the request
        data = request.get_json()
        user_name = data.get('user_name')
        email = data.get('email')

        # Validate the input data
        if not user_name or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if the new username or email already exists
        existing_user = User.query.filter(
            (User.user_name == user_name) | (User.email == email)).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username or email already in use'}), 400

        # Update the user profile
        user.user_name = user_name
        user.email = email

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        # Rollback in case of a database error
        db.session.rollback()

        # Log the error for debugging (again, you might log to a file)
        print(f"Error in edit_profile: {e}")

        return jsonify({'error': 'An unexpected error occurred'}), 500

