import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())
try:
    from ML.recommender import recommender
    from db import get_db_connection
except ImportError:
    # Fallback if running directly in ML dir
    sys.path.append(os.path.join(os.getcwd(), 'Backend'))
    from ML.recommender import recommender
    from db import get_db_connection

def verify_rec():
    user_id = 1
    print(f"Generating recommendations for User {user_id}...")
    
    try:
        top_ids = recommender.get_top_n(user_id, n=5)
        print(f"Top IDs: {top_ids}")
        
        if top_ids:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            format_strings = ','.join(['%s'] * len(top_ids))
            cursor.execute(f"SELECT id, item_name, category FROM Menu WHERE id IN ({format_strings})", tuple(top_ids))
            items = cursor.fetchall()
            
            # Sort by order of top_ids
            item_map = {item['id']: item for item in items}
            ordered_items = [item_map[mid] for mid in top_ids if mid in item_map]
            
            print("\nRecommended Items:")
            for item in ordered_items:
                print(f"- {item['item_name']} ({item['category']})")
                
            cursor.close()
            conn.close()
        else:
            print("No recommendations generated.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_rec()
