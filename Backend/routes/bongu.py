from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
from db import get_db_connection  # Import centralized DB connection function

bongu_auth = Blueprint('bongu_auth', __name__)
bcrypt = Bcrypt()

@bongu_auth.route('/login', methods=['GET', 'POST'])
def bongu_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']

        # Create a new database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if action == "register":
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                try:
                    cursor.execute("INSERT INTO Bongus (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
                    conn.commit()
                    return "Bongu registered successfully! <a href='/bongu/login'>Login</a>"
                except mysql.connector.IntegrityError:
                    return "Username already exists. <a href='/bongu/login'>Try again</a>"

            elif action == "login":
                cursor.execute("SELECT id, password_hash FROM Bongus WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and bcrypt.check_password_hash(user[1], password):
                    session['bongu_id'] = user[0]
                    session['bongu_username'] = username
                    print(f"Logged in: {session}")
                    return redirect(url_for('bongu_auth.bongu_orders'))
                else:
                    return "Invalid credentials. <a href='/bongu/login'>Try again</a>"

        finally:
            cursor.close()
            conn.close()  # Ensure connection is closed

    return render_template("bongu-login.html")

@bongu_auth.route('/bongu-dashboard')
def bongu_dashboard():
    if 'bongu_id' in session:
        return render_template('bongu-main.html', username=session.get('bongu_username'))
    return redirect(url_for('bongu_auth.bongu_login'))

@bongu_auth.route('/orders')
def bongu_orders():
    if 'bongu_id' not in session:
        print("Redirecting to bongu_login: No bongu_id in session")
        return redirect(url_for('bongu_auth.bongu_login'))

    print(f"Fetching orders for bongu_id: {session['bongu_id']}")
    # Create a new database connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch available orders (restaurant_accepted, not yet accepted by any Bongu)
        cursor.execute("""
            SELECT o.id, o.status, o.total_price, o.order_date, r.name AS restaurant_name,
                   u.name AS customer_name,
                   a.apartment_no, a.apartment_name, a.landmark, a.road_no, a.locality, a.city, a.state
            FROM Orders o
            JOIN Restaurants r ON o.restaurant_id = r.id
            JOIN Users u ON o.user_id = u.id
            LEFT JOIN Address a ON o.user_id = a.user_id
            WHERE o.status = 'restaurant_accepted' AND o.bongu_id IS NULL

        """)
        available_orders = cursor.fetchall()

        # Fetch accepted orders (bongu_accepted, preparing, out_for_delivery) assigned to this Bongu
        cursor.execute("""
            SELECT o.id, o.status, o.total_price, o.order_date, r.name AS restaurant_name,
                   u.name AS customer_name,
                   a.apartment_no, a.apartment_name, a.landmark, a.road_no, a.locality, a.city, a.state
            FROM Orders o
            JOIN Restaurants r ON o.restaurant_id = r.id
            JOIN Users u ON o.user_id = u.id
            LEFT JOIN Address a ON o.user_id = a.user_id
            WHERE o.bongu_id = %s AND o.status IN ('bongu_accepted', 'preparing', 'out_for_delivery')
        """, (session['bongu_id'],))
        accepted_orders = cursor.fetchall()

        # Process both sets of orders
        for order in available_orders + accepted_orders:
            order['bongu_payment'] = round(float(order['total_price']) * 0.20, 2)
            if order['apartment_no']:
                order['full_address'] = (
                    f"{order['apartment_no']}, {order['apartment_name']}, "
                    f"{order['road_no']}, {order['locality']}, "
                    f"{order['city']}, {order['state']}"
                    f"{', Landmark: ' + order['landmark'] if order['landmark'] else ''}"
                )
            else:
                order['full_address'] = "Address not provided"

        print(f"Available orders: {available_orders}")
        print(f"Accepted orders: {accepted_orders}")
        return render_template('bongu-main.html', available_orders=available_orders, accepted_orders=accepted_orders, bongu_id=session['bongu_id'])
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()  # Ensure connection is closed

@bongu_auth.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    if 'bongu_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    # Create a new database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, bongu_id FROM Orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order or order[0] != 'restaurant_accepted' or order[1] is not None:
            return jsonify({"error": "Order not found, already accepted, or not ready for acceptance"}), 403

        cursor.execute("""
            UPDATE Orders 
            SET status = 'bongu_accepted', bongu_id = %s 
            WHERE id = %s
        """, (session['bongu_id'], order_id))
        conn.commit()
        return jsonify({"message": "Order accepted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()  # Ensure connection is closed

@bongu_auth.route('/update_delivery/<int:order_id>', methods=['POST'])
def update_delivery(order_id):
    if 'bongu_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    status = request.form.get('status')
    valid_statuses = ['preparing', 'out_for_delivery', 'delivered', 'failed']
    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    # Create a new database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verify the order is assigned to this Bongu and in a valid state
        cursor.execute("SELECT status, bongu_id FROM Orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Order not found"}), 404
        if result[1] != session['bongu_id'] or result[0] not in ('bongu_accepted', 'preparing', 'out_for_delivery'):
            return jsonify({"error": "Order not assigned to you or not in a state to update"}), 403

        # Map form status to database status
        order_status = status  # Use the form value directly since it's in the ENUM
        if status == 'delivered':
            order_status = 'delivered'
        elif status == 'failed':
            order_status = 'canceled'

        # Update Orders table
        cursor.execute("UPDATE Orders SET status = %s WHERE id = %s", (order_status, order_id))

        # Update or insert into Delivery table
        cursor.execute("SELECT id FROM Delivery WHERE order_id = %s", (order_id,))
        delivery = cursor.fetchone()
        if delivery:
            if order_status in ('delivered', 'canceled'):  # 'canceled' corresponds to 'failed'
                cursor.execute("""
                    UPDATE Delivery SET delivery_status = %s, delivery_time = CURRENT_TIMESTAMP
                    WHERE order_id = %s
                """, (order_status, order_id))
            else:
                cursor.execute("""
                    UPDATE Delivery SET delivery_status = %s, delivery_time = NULL
                    WHERE order_id = %s
                """, (order_status, order_id))
        else:
            if order_status in ('delivered', 'canceled'):
                cursor.execute("""
                    INSERT INTO Delivery (order_id, delivery_status, driver_id, delivery_time)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (order_id, order_status, session['bongu_id']))
            else:
                cursor.execute("""
                    INSERT INTO Delivery (order_id, delivery_status, driver_id, delivery_time)
                    VALUES (%s, %s, %s, NULL)
                """, (order_id, order_status, session['bongu_id']))

        conn.commit()
        return jsonify({"message": "Delivery status updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()  # Ensure connection is closed