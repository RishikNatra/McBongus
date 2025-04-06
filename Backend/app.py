from flask import Flask, jsonify, render_template, session, redirect, url_for, request  
from flask_bcrypt import Bcrypt
from flask_session import Session
import mysql.connector
from routes.restaurant import restaurant_auth
from routes.menu import menu_bp
from routes.bongu import bongu_auth 
from routes.auth import auth

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Secret key for session handling
app.secret_key = 'your_secret_key'

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database connection
def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishik@1429145",
        database="McBongus_DB"
    )

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(bongu_auth, url_prefix='/bongu')
app.register_blueprint(restaurant_auth, url_prefix='/restaurant')
app.register_blueprint(menu_bp, url_prefix='/menu')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/restaurants')
def restaurants():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/user-login')
def user_login():
    return render_template('user-login.html')

@app.route('/bongu-login')
def bongu_login():
    return render_template('bongu-login.html')

@app.route('/restaurant-login')
def restaurant_login():
    return render_template('restaurant-login.html')

@app.route('/restaurant/<int:restaurant_id>')
def restaurant(restaurant_id):
    # Get restaurant details and menu items
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM MENU WHERE restaurant_id = %s AND availability = 1", (restaurant_id,))
    menu_items = cursor.fetchall()
    cursor.execute("SELECT name, rating FROM RESTAURANT WHERE id = %s", (restaurant_id,))
    restaurant_details = cursor.fetchone()
    conn.close()

    if restaurant_details:
        return render_template('restaurant_page.html', restaurant_id=restaurant_id, 
                               restaurant_name=restaurant_details[0], rating=restaurant_details[1],
                               menu_items=menu_items)
    else:
        return "Restaurant not found", 404

@app.route('/menu/<int:restaurant_id>')
def get_menu(restaurant_id):
    conn = db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, item_name, price, availability FROM MENU WHERE restaurant_id = %s", (restaurant_id,))
        menu_items = cursor.fetchall()
        
        if not menu_items:
            return jsonify({"error": "No menu items found"})
        
        return jsonify(menu_items)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        restaurant_id = data.get('restaurant_id')
        items = data.get('items')
        total_price = data.get('total_price')

        if not all([restaurant_id, items, total_price]):
            return jsonify({"error": "Missing required fields"}), 400

        conn = db()
        cursor = conn.cursor()

        # Insert into Orders table
        cursor.execute("""
            INSERT INTO Orders (user_id, restaurant_id, total_price, status)
            VALUES (%s, %s, %s, 'pending')
        """, (session['user_id'], restaurant_id, total_price))
        order_id = cursor.lastrowid

        # Insert into Order_Items table
        for item in items:
            cursor.execute("""
                INSERT INTO Order_Items (order_id, menu_id, quantity, price)
                VALUES (%s, %s, %s, (SELECT price FROM Menu WHERE id = %s))
            """, (order_id, item['menu_id'], item['quantity'], item['menu_id']))

        # Simulate payment
        cursor.execute("""
            INSERT INTO Payments (order_id, payment_status, transaction_id)
            VALUES (%s, 'completed', %s)
        """, (order_id, f"TXN{order_id}"))

        conn.commit()  # Ensure the transaction is committed
        print(f"Order {order_id} committed to database")
        cursor.close()
        conn.close()
        return jsonify({"message": "Order placed successfully", "order_id": order_id}), 200
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/order_status/<int:order_id>')
def order_status(order_id):
    conn = db()
    cursor = conn.cursor(dictionary=True)

    # Fetch the order details
    cursor.execute("""
        SELECT o.id, o.total_price, o.status, o.order_date, r.name AS restaurant_name,
               d.delivery_status, d.delivery_time
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.id
        LEFT JOIN Delivery d ON o.id = d.order_id
        WHERE o.id = %s
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        cursor.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    # Map status to user-friendly message
    status_messages = {
        'pending': 'pending',
        'restaurant_accepted': 'restaurant_accepted',
        'canceled_awaiting_refund': 'canceled_awaiting_refund',
        'bongu_accepted': 'bongu_accepted',
        'delivered': 'delivered',
        'canceled': 'canceled'
    }

    order_details = {
        'id': order['id'],
        'restaurant_name': order['restaurant_name'],
        'total_price': float(order['total_price']),  # Convert Decimal to float for JSON
        'status': status_messages.get(order['status'], 'Unknown status'),
        'delivery_status': order['delivery_status'] if order['delivery_status'] else 'Not assigned',
        'delivery_time': order['delivery_time'].isoformat() if order['delivery_time'] else 'Pending'
    }

    cursor.close()
    conn.close()

    return jsonify(order_details)

@app.route('/order_tracking/<int:order_id>')
def order_tracking(order_id):
    return render_template('order_tracking.html')

if __name__ == '__main__':
    app.run(debug=True)
