
from app import app
from db import get_db_connection

def verify_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("Checking Restaurants and their Menu count:")
    cursor.execute("SELECT id, name FROM Restaurants")
    restaurants = cursor.fetchall()
    
    for r in restaurants:
        r_id = r['id']
        r_name = r['name']
        
        cursor.execute("SELECT count(*) as cnt FROM Menu WHERE restaurant_id = %s", (r_id,))
        count = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT item_name FROM Menu WHERE restaurant_id = %s LIMIT 1", (r_id,))
        first_item = cursor.fetchone()
        item_name = first_item['item_name'] if first_item else "None"
        
        print(f"ID: {r_id} | Name: {r_name} | Menu Items: {count} | Sample: {item_name}")

if __name__ == "__main__":
    verify_data()
