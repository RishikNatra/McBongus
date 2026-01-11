
import sys
import os
# Ensure we can import from current directory
sys.path.append(os.getcwd())

try:
    from ML.trainer import train_model
    from ML.recommender import recommender
    from db import get_db_connection
except ImportError as e:
    print(f"Import Error: {e}")
    print("Run this script from McBongus/Backend directory")
    sys.exit(1)

def verify():
    print("--- 1. Running Training ---")
    try:
        train_model()
    except Exception as e:
        print(f"Training failed: {e}")
        return

    print("\n--- 2. Testing Inference ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users LIMIT 1")
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id = user[0]
        print(f"Testing for User ID: {user_id}")
        
        # Reload model to ensure we picked up the fresh one
        recommender.load_model()
        
        try:
            recs = recommender.get_top_n(user_id, n=5)
            print(f"Recommendations (Menu IDs): {recs}")
            
            if recs:
                print("SUCCESS: Got recommendations.")
            else:
                print("WARNING: Got empty recommendations (User might not have history or sparse data).")
        except Exception as e:
            print(f"Inference failed: {e}")
    else:
        print("No users found in DB to test inference.")

if __name__ == "__main__":
    verify()
