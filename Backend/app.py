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
        SELECT o.id, o.total_price, o.status, o.order_date, o.bongu_id, r.name AS restaurant_name,
               d.delivery_status, d.delivery_time, b.username as bongu_name
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.id
        LEFT JOIN Delivery d ON o.id = d.order_id
        LEFT JOIN Bongus b ON o.bongu_id = b.id 
        WHERE o.id = %s
    """, (order_id,))
    order = cursor.fetchone()

    if not order:
        cursor.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    order_details = {
        'id': order['id'],
        'restaurant_name': order['restaurant_name'],
        'total_price': float(order['total_price']),  # Convert Decimal to float for JSON
        'status': order['status'],  # Return raw status from Orders table
        'delivery_status': order['delivery_status'] if order['delivery_status'] else 'Not assigned',
        'delivery_time': order['delivery_time'].isoformat() if order['delivery_time'] else 'Pending',
        'bongu_name': order['bongu_name'] if order['bongu_name'] else 'Not yet assigned'
    }

    cursor.close()
    conn.close()

    return jsonify(order_details)

@app.route('/order_tracking/<int:order_id>')
def order_tracking(order_id):
    conn = db()
    cursor = conn.cursor(dictionary=True)

    # Fetch order details including restaurant name and delivery info
    cursor.execute("""
        SELECT o.id, o.total_price, o.status, o.order_date, o.bongu_id,
               r.name AS restaurant_name,
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
        return "Order not found", 404

    # Fetch Bongu name if bongu_id exists
    bongu_name = None
    if order['bongu_id']:
        cursor.execute("SELECT username FROM Bongus WHERE id = %s", (order['bongu_id'],))
        bongu = cursor.fetchone()
        bongu_name = bongu['username'] if bongu else None

    cursor.close()
    conn.close()

    # Render the template with order details and bongu_name
    return render_template('order_tracking.html', 
                          order=order, 
                          bongu_name=bongu_name)

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    conn = db()
    cursor = conn.cursor()
    try:
        # Verify the order belongs to the user and is cancellable
        cursor.execute("SELECT user_id, status FROM Orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({"error": "Order not found"}), 404
        if order[0] != session['user_id']:
            return jsonify({"error": "You can only cancel your own orders"}), 403
        
        cancellable_statuses = ['pending', 'restaurant_accepted', 'bongu_accepted']
        if order[1] not in cancellable_statuses:
            return jsonify({"error": "Order cannot be canceled at this stage"}), 403

        # Update order status to 'canceled'
        cursor.execute("UPDATE Orders SET status = 'canceled' WHERE id = %s", (order_id,))
        
        # Update Delivery table if it exists
        cursor.execute("SELECT id FROM Delivery WHERE order_id = %s", (order_id,))
        delivery = cursor.fetchone()
        if delivery:
            cursor.execute("UPDATE Delivery SET delivery_status = 'canceled' WHERE order_id = %s", (order_id,))

        conn.commit()
        return jsonify({"message": "Order canceled successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
@app.route('/get_address', methods=['GET'])
def get_address():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    conn = db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Address WHERE user_id = %s", (session['user_id'],))
        address = cursor.fetchone()
        if address:
            return jsonify(address)
        else:
            return jsonify({"message": "No address found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update or insert the user's address
@app.route('/update_address', methods=['POST'])
def update_address():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    apartment_no = data.get('apartment_no')
    apartment_name = data.get('apartment_name')
    landmark = data.get('landmark')
    road_no = data.get('road_no')
    locality = data.get('locality')
    city = data.get('city')
    state = data.get('state')

    if not all([apartment_no, apartment_name, road_no, locality, city, state]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = db()
    cursor = conn.cursor()
    try:
        # Check if address exists for the user
        cursor.execute("SELECT id FROM Address WHERE user_id = %s", (session['user_id'],))
        existing_address = cursor.fetchone()

        if existing_address:
            # Update existing address
            cursor.execute("""
                UPDATE Address 
                SET apartment_no = %s, apartment_name = %s, landmark = %s, road_no = %s, 
                    locality = %s, city = %s, state = %s 
                WHERE user_id = %s
            """, (apartment_no, apartment_name, landmark, road_no, locality, city, state, session['user_id']))
        else:
            # Insert new address
            cursor.execute("""
                INSERT INTO Address (user_id, apartment_no, apartment_name, landmark, road_no, locality, city, state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], apartment_no, apartment_name, landmark, road_no, locality, city, state))

        conn.commit()
        return jsonify({"message": "Address updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
