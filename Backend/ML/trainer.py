
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
    
    # 1. Fetch User Interaction Data (Collaborative Filtering)
    query_interactions = """
        SELECT o.user_id, oi.menu_id, SUM(oi.quantity) as quantity
        FROM Orders o
        JOIN Order_Items oi ON o.id = oi.order_id
        GROUP BY o.user_id, oi.menu_id
    """
    
    # 2. Fetch Menu Item Data (Content-Based Filtering)
    query_items = "SELECT id, category FROM Menu"

    print("Fetching data...")
    cursor.execute(query_interactions)
    interactions_data = cursor.fetchall()

    cursor.execute(query_items)
    items_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not interactions_data:
        print("No interaction data found. Creating basic category similarity model...")
        # Even if no orders, we can build a category-based model
        if not items_data:
            print("No menu items found. Cannot train.")
            return

    print(f"Fetched {len(interactions_data)} interactions and {len(items_data)} menu items.")
    
    # --- Collaborative Filtering (User-Item Matrix) ---
    collab_sim_df = None
    all_menu_ids = [item['id'] for item in items_data]
    
    if interactions_data:
        df_interactions = pd.DataFrame(interactions_data)
        # Ensure all menu items are columns, even if no interactions
        # pivot_table might miss items with no sales
        user_item_matrix = df_interactions.pivot_table(index='user_id', columns='menu_id', values='quantity').fillna(0)
        
        # Re-index to include all known menu items (fill 0 for unseen items)
        # This aligns the matrix dimensions for combination later
        user_item_matrix = user_item_matrix.reindex(columns=all_menu_ids, fill_value=0)
        
        # Item-Item Similarity (transpose so rows are items)
        item_user_matrix = user_item_matrix.T
        collab_sim_matrix = cosine_similarity(item_user_matrix)
        collab_sim_df = pd.DataFrame(collab_sim_matrix, index=item_user_matrix.index, columns=item_user_matrix.index)
        print("Collaborative model built.")
    else:
        # If no interactions, collab similarity is all zeros
        collab_sim_df = pd.DataFrame(0, index=all_menu_ids, columns=all_menu_ids)
        print("No interactions. Collaborative model is empty.")

    # --- Content-Based Filtering (Category Match) ---
    # Create a feature matrix where rows=items, columns=categories (One-Hot Encoding) or direct exact match
    df_items = pd.DataFrame(items_data)
    
    if not df_items.empty:
        # Helper to create similarity based on category match: 1 if same category, 0 otherwise
        # Using One-Hot Encoding for simple dot product equivalent to "same category" check
        # But easier: just iterate? No, matrix ops are faster.
        # Let's use pandas get_dummies
        category_matrix = pd.get_dummies(df_items.set_index('id')['category'])
        
        # Reindex to ensure order matches all_menu_ids
        category_matrix = category_matrix.reindex(all_menu_ids).fillna(0) # In case an ID was missing? Should be fine.
        
        # Calculate cosine similarity (or dot product for binary vectors)
        # Cosine similarity of binary vectors:
        # (A . B) / (|A|*|B|)
        # Since each item has exactly 1 category, |A| = 1, |B| = 1.
        # So Cosine Sim = 1 if same category, 0 else.
        content_sim_matrix = cosine_similarity(category_matrix)
        content_sim_df = pd.DataFrame(content_sim_matrix, index=category_matrix.index, columns=category_matrix.index)
        print("Content-based model built.")
    else:
        content_sim_df = pd.DataFrame(0, index=all_menu_ids, columns=all_menu_ids)

    # --- Hybrid Model (Weighted Combination) ---
    # Weights for blending
    ALPHA = 0.7 # Weight for Collaborative (User Behavior)
    BETA = 0.3  # Weight for Content (Category Similarity)
    
    if not interactions_data:
        # If no sales data, rely 100% on categories
        ALPHA, BETA = 0.0, 1.0
        print("Using Content-Only mode (Cold Start).")

    # Ensure indices align (they should, both are all_menu_ids)
    final_sim_df = (ALPHA * collab_sim_df) + (BETA * content_sim_df)
    
    # Save model
    print(f"Saving hybrid model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(final_sim_df, f)
        
    print("Training complete.")

if __name__ == "__main__":
    train_model()
