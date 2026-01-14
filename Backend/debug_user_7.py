import sys
import os
import pandas as pd

# Add parent directory to path to import db.py
sys.path.append(os.getcwd())
try:
    from db import get_db_connection
except ImportError:
    pass

def debug_user():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print("--- User 7 Orders ---")
    cursor.execute("""
        SELECT o.id, o.order_date, oi.quantity, m.item_name, m.category, m.id as menu_id
        FROM Orders o
        JOIN Order_Items oi ON o.id = oi.order_id
        JOIN Menu m ON oi.menu_id = m.id
        WHERE o.user_id = 7
    """)
    orders = cursor.fetchall()
    for o in orders:
        print(o)

    print("\n--- All Categories in Menu ---")
    cursor.execute("SELECT DISTINCT category FROM Menu")
    cats = cursor.fetchall()
    print([c['category'] for c in cats])
    
    print("\n--- Items in 'Pizza' Category (Case Insensitive) ---")
    cursor.execute("SELECT id, item_name, category FROM Menu WHERE LOWER(category) LIKE '%pizza%'")
    pizzas = cursor.fetchall()
    for p in pizzas:
        print(p)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug_user()
