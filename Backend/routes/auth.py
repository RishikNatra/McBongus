from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import mysql.connector
from db import get_db_connection  # Import the centralized DB connection function

auth = Blueprint('auth', __name__)  # Define blueprint
bcrypt = Bcrypt()

# User Login & Registration
@auth.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

        # Create a new database connection
        db = get_db_connection()
        cursor = db.cursor()

        try:
            if action == "register":
                name = request.form['name']
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                try:
                    cursor.execute("INSERT INTO Users (name, username, password_hash) VALUES (%s, %s, %s)", (name, username, hashed_password))
                    db.commit()
                    return "User registered successfully! <a href='/auth/user-login'>Login</a>"
                except mysql.connector.IntegrityError:
                    return "Username already exists. <a href='/auth/user-login'>Try again</a>"

            elif action == "login":
                cursor.execute("SELECT id, password_hash FROM Users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and bcrypt.check_password_hash(user[1], password):
                    session['user_id'] = user[0]  # Store user ID
                    session['username'] = username  # Store username
                    return redirect(url_for('auth.user_dashboard'))  # Redirect to dashboard
                else:
                    return "Invalid credentials. <a href='/auth/user-login'>Try again</a>"

        finally:
            cursor.close()
            db.close()  # Ensure connection is closed

    return render_template("user-login.html")

# User Dashboard
@auth.route("/dashboard")
def user_dashboard():
    # Create a new database connection
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    try:
        cursor.execute("SELECT * FROM Restaurants")  # Fetch restaurant data
        restaurants = cursor.fetchall()
        return render_template("main.html", username=session.get("username"), restaurants=restaurants)
    finally:
        cursor.close()
        db.close()  # Ensure connection is closed

# Logout
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.user_login'))  # Redirect to login page

# Menu Blueprint
menu = Blueprint('menu', __name__)

@menu.route("/menu/<restaurant_name>")
def get_menu(restaurant_name):
    # Create a new database connection
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Menu WHERE restaurant_id = (SELECT id FROM Restaurants WHERE name = %s)", (restaurant_name,))
        menu_items = cursor.fetchall()
        return render_template("menu.html", restaurant_name=restaurant_name, menu_items=menu_items)
    finally:
        cursor.close()
        db.close()  # Ensure connection is closed