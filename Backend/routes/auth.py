from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from flask_bcrypt import Bcrypt

auth = Blueprint('auth', __name__)  # ✅ Define blueprint first
bcrypt = Bcrypt()

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rishik@1429145",
    database="McBongus_DB"
)
cursor = db.cursor()

# User Login & Registration
@auth.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

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
                return redirect(url_for('auth.user_dashboard'))  # ✅ Redirect to dashboard
            else:
                return "Invalid credentials. <a href='/auth/user-login'>Try again</a>"

    return render_template("user-login.html")

# User Dashboard
@auth.route("/dashboard")
def user_dashboard():
    cursor = db.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT * FROM Restaurants")  # Fetch restaurant data
    restaurants = cursor.fetchall()  
    cursor.close()

    return render_template("main.html", username=session["username"], restaurants=restaurants)

# Logout
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.user_login'))  # ✅ Redirect to login page

menu = Blueprint('menu', __name__)

@menu.route("/menu/<restaurant_name>")
def get_menu(restaurant_name):
    # Fetch menu items from the database
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Menu WHERE restaurant_id = (SELECT id FROM Restaurants WHERE name = %s)", (restaurant_name,))
    menu_items = cursor.fetchall()
    cursor.close()

    return render_template("menu.html", restaurant_name=restaurant_name, menu_items=menu_items)
