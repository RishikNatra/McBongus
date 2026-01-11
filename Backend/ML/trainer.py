
import os
import sys
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector

# Add parent directory to path to import db.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db import get_db_connection
except ImportError:
    # Fallback if running from Backend directory
    sys.path.append(os.getcwd())
    from db import get_db_connection

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'recommendation_model.pkl')

def train_model():
    print("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT o.user_id, oi.menu_id, SUM(oi.quantity) as quantity
        FROM Orders o
        JOIN Order_Items oi ON o.id = oi.order_id
        GROUP BY o.user_id, oi.menu_id
    """
    
    print("Fetching data...")
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not data:
        print("No data found to train model.")
        return

    print(f"Fetched {len(data)} records.")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create User-Item Matrix
    # Rows: Users, Columns: Items (Menu IDs)
    user_item_matrix = df.pivot_table(index='user_id', columns='menu_id', values='quantity').fillna(0)
    
    print(f"User-Item Matrix shape: {user_item_matrix.shape}")
    
    # We want Item-Item similarity
    # Transpose so Rows are Items
    item_user_matrix = user_item_matrix.T
    
    print("Calculating Cosine Similarity...")
    # Calculate similarity
    similarity_matrix = cosine_similarity(item_user_matrix)
    
    # Convert to DataFrame for easier lookup
    similarity_df = pd.DataFrame(similarity_matrix, index=item_user_matrix.index, columns=item_user_matrix.index)
    
    # Save model
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(similarity_df, f)
        
    print("Training complete.")

if __name__ == "__main__":
    train_model()
