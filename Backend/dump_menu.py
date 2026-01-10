
from app import app
from db import get_db_connection
import json

def dump_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Menu")
    items = cursor.fetchall()
    
    # Organize by restaurant
    by_rest = {}
    for item in items:
        rid = item['restaurant_id']
        if rid not in by_rest:
            by_rest[rid] = []
        by_rest[rid].append(item['item_name'])
        
    print(json.dumps(by_rest, indent=2))

if __name__ == "__main__":
    dump_menu()
