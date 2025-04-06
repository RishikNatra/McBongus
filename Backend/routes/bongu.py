# routes/bongu.py
from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector

bongu_auth = Blueprint('bongu_auth', __name__)

def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishik@1429145",
        database="mcbongus_db"
    )

bcrypt = Bcrypt()

@bongu_auth.route('/login', methods=['GET'])
def bongu_login():
    print("Rendering bongu login page")
    return render_template('bongu-login.html')

@bongu_auth.route('/login', methods=['POST'])
def bongu_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"Bongu login attempt: username={username}")
    conn = db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, password_hash FROM Bongus WHERE username = %s", (username,))
    bongu = cursor.fetchone()
    cursor.close()
    conn.close()

    if bongu and bcrypt.check_password_hash(bongu['password_hash'], password):
        session['bongu_id'] = bongu['id']
        print(f"Bongu logged in: bongu_id = {bongu['id']}")
        return redirect(url_for('bongu_auth.bongu_orders'))
    print("Bongu login failed")
    return "Login failed", 401

@bongu_auth.route('/orders')
def bongu_orders():
    if 'bongu_id' not in session:
        print("Redirecting to bongu_login: No bongu_id in session")
        return redirect(url_for('bongu_auth.bongu_login'))
    
    print(f"Fetching orders for bongu_id: {session['bongu_id']}")
    try:
        conn = db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        print(f"Current database: {current_db}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Tables in database: {tables}")

        # Fetch orders with status 'restaurant_accepted' (available to accept)
        # OR orders with status 'bongu_accepted' that are assigned to this Bongu
        cursor.execute("""
            SELECT o.id, o.status, o.total_price, o.order_date, r.name AS restaurant_name,
                   u.name AS customer_name, d.driver_id
            FROM Orders o
            JOIN Restaurants r ON o.restaurant_id = r.id
            JOIN Users u ON o.user_id = u.id
            LEFT JOIN Delivery d ON o.id = d.order_id
            WHERE o.status = 'restaurant_accepted'
               OR (o.status = 'bongu_accepted' AND d.driver_id = %s)
        """, (session['bongu_id'],))
        orders = cursor.fetchall()
        print(f"Orders fetched: {orders}")

        cursor.close()
        conn.close()
        return render_template('bongu-main.html', orders=orders, bongu_id=session['bongu_id'])
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@bongu_auth.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    if 'bongu_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = db()
    cursor = conn.cursor()
    try:
        # Verify the order is in 'restaurant_accepted' status
        cursor.execute("SELECT status FROM Orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order or order[0] != 'restaurant_accepted':
            return jsonify({"error": "Order not found or not ready for Bongu acceptance"}), 403

        # Check if the order is already assigned to another delivery partner
        cursor.execute("SELECT driver_id FROM Delivery WHERE order_id = %s", (order_id,))
        existing_driver = cursor.fetchone()
        if existing_driver and existing_driver[0] != session['bongu_id']:
            return jsonify({"error": "Order already assigned to another delivery partner"}), 403

        # Assign the order to the Bongu and update the status to 'bongu_accepted'
        cursor.execute("""
            INSERT INTO Delivery (order_id, driver_id, delivery_status)
            VALUES (%s, %s, 'assigned')
            ON DUPLICATE KEY UPDATE driver_id = %s, delivery_status = 'assigned'
        """, (order_id, session['bongu_id'], session['bongu_id']))
        cursor.execute("UPDATE Orders SET status = 'bongu_accepted' WHERE id = %s", (order_id,))
        conn.commit()
        return jsonify({"message": "Order accepted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@bongu_auth.route('/update_delivery/<int:order_id>', methods=['POST'])
def update_delivery(order_id):
    if 'bongu_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    status = request.form.get('status')
    valid_statuses = ['preparing', 'out_for_delivery', 'delivered', 'failed']
    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    conn = db()
    cursor = conn.cursor()
    try:
        # Verify the order is assigned to this Bongu and is in 'bongu_accepted' status
        cursor.execute("""
            SELECT o.status, d.driver_id
            FROM Orders o
            JOIN Delivery d ON o.id = d.order_id
            WHERE o.id = %s
        """, (order_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Order not found or no delivery record"}), 404
        if result[0] != 'bongu_accepted':
            return jsonify({"error": "Order is not in a state to update delivery status"}), 403
        if result[1] != session['bongu_id']:
            return jsonify({"error": "You are not assigned to this order"}), 403

        # Map delivery_status to order_status
        order_status = {
            'preparing': 'bongu_accepted',  # Still in preparation
            'out_for_delivery': 'bongu_accepted',  # Still in delivery
            'delivered': 'delivered',
            'failed': 'canceled'
        }.get(status)

        # Update the Delivery table
        cursor.execute("""
            UPDATE Delivery 
            SET delivery_status = %s, delivery_time = NOW()
            WHERE order_id = %s AND driver_id = %s
        """, (status, order_id, session['bongu_id']))

        # Check if the Delivery update affected any rows
        if cursor.rowcount == 0:
            return jsonify({"error": "Failed to update delivery status: No matching delivery record"}), 500

        # Update the Orders table
        cursor.execute("""
            UPDATE Orders 
            SET status = %s 
            WHERE id = %s
        """, (order_status, order_id))

        conn.commit()
        return jsonify({"message": "Delivery status updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()