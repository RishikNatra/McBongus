# routes/restaurant.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from flask_bcrypt import Bcrypt

restaurant_auth = Blueprint('restaurant_auth', __name__)

bcrypt = Bcrypt()

def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishik@1429145",
        database="McBongus_DB"
    )

@restaurant_auth.route('/restaurant-login', methods=['GET', 'POST'])
def restaurant_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

        if action == "login":
            conn = db()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Restaurants WHERE username = %s", (username,))
            restaurant = cursor.fetchone()

            if not restaurant:
                cursor.close()
                conn.close()
                return "Restaurant not found. <a href='/restaurant/restaurant-login'>Try again</a>"

            cursor.execute("SELECT password_hash FROM RestaurantRequests WHERE username = %s", (username,))
            request_user = cursor.fetchone()

            if request_user and bcrypt.check_password_hash(request_user[0], password):
                session['restaurant_id'] = restaurant[0]
                session['restaurant_name'] = username
                cursor.close()
                conn.close()
                return redirect(url_for('restaurant_auth.restaurant_dashboard'))
            else:
                cursor.close()
                conn.close()
                return "Invalid credentials. <a href='/restaurant/restaurant-login'>Try again</a>"

    return render_template("restaurant-login.html")

@restaurant_auth.route('/restaurant-dashboard')
def restaurant_dashboard():
    if 'restaurant_id' not in session:
        return redirect(url_for('restaurant_auth.restaurant_login'))

    conn = db()
    cursor = conn.cursor()

    # Fetch restaurant details
    cursor.execute("SELECT name, location, username, rating FROM Restaurants WHERE id = %s", (session['restaurant_id'],))
    restaurant = cursor.fetchone()

    if not restaurant:
        cursor.close()
        conn.close()
        return "Restaurant not found. <a href='/restaurant/restaurant-logout'>Logout</a>"

    restaurant_details = {
        'name': restaurant[0],
        'location': restaurant[1],
        'username': restaurant[2],
        'rating': restaurant[3]
    }

    # Fetch pending orders
    cursor.execute("""
        SELECT id, user_id, total_price, order_date, status
        FROM Orders
        WHERE restaurant_id = %s AND status = 'pending'
    """, (session['restaurant_id'],))
    pending_orders = cursor.fetchall()

    # Fetch order items for each pending order
    order_details = {}
    for order in pending_orders:
        order_id = order[0]
        cursor.execute("""
            SELECT oi.quantity, m.item_name, m.price
            FROM Order_Items oi
            JOIN Menu m ON oi.menu_id = m.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        order_details[order_id] = items  # Store items as (quantity, item_name, price) tuples

    cursor.close()
    conn.close()

    return render_template("restaurant-main.html", restaurant=restaurant_details, orders=pending_orders, order_details=order_details)

@restaurant_auth.route('/restaurant/order-action/<int:order_id>', methods=['POST'])
def order_action(order_id):
    if 'restaurant_id' not in session:
        return redirect(url_for('restaurant_auth.restaurant_login'))

    action = request.form.get('action')

    conn = db()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM Orders WHERE id = %s AND restaurant_id = %s", (order_id, session['restaurant_id']))
    order = cursor.fetchone()

    if not order or order[0] != 'pending':
        cursor.close()
        conn.close()
        return "Order not found or already processed. <a href='/restaurant/restaurant-dashboard'>Back to Dashboard</a>"

    if action == 'accept':
        new_status = 'restaurant_accepted'
    elif action == 'reject':
        new_status = 'canceled_awaiting_refund'
    else:
        cursor.close()
        conn.close()
        return "Invalid action. <a href='/restaurant/restaurant-dashboard'>Back to Dashboard</a>"

    cursor.execute("UPDATE Orders SET status = %s WHERE id = %s", (new_status, order_id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('restaurant_auth.restaurant_dashboard'))

@restaurant_auth.route('/restaurant-register', methods=['GET', 'POST'])
def restaurant_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        contact = request.form['contact']
        location = request.form['location']
        password = request.form['password']
        action = request.form['action']

        if action == "register":
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            conn = db()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO RestaurantRequests (id, name, username, location, contact, password_hash)
                    VALUES (NULL, %s, %s, %s, %s, %s)
                """, (name, username, location, contact, hashed_password))
                conn.commit()
                cursor.close()
                conn.close()
                return "You have successfully requested to register your restaurant. We will conduct an extensive review of your restaurant and verify your request soon."
            except mysql.connector.IntegrityError as e:
                cursor.close()
                conn.close()
                if "contact" in str(e):
                    return "Contact already exists in a pending request. <a href='/restaurant/restaurant-register'>Try again</a>"
                elif "username" in str(e):
                    return "Username already exists in a pending request. <a href='/restaurant/restaurant-register'>Try again</a>"
                return f"Error: {str(e)}. <a href='/restaurant/restaurant-register'>Try again</a>"
            except Exception as e:
                cursor.close()
                conn.close()
                return f"Error: {str(e)}. <a href='/restaurant/restaurant-register'>Try again</a>"

    return render_template("restaurant-register.html")

@restaurant_auth.route('/restaurant-logout')
def restaurant_logout():
    session.clear()
    return redirect(url_for('restaurant_auth.restaurant_login'))