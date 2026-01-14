
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
    # Create a feature matrix where rows=items, columns=categories (One-Hot Encoding)
    df_items = pd.DataFrame(items_data)
    
    content_sim_df = None
    item_category_map = {} # Map item_id -> category_name
    
    if not df_items.empty:
        # Helper to create similarity based on category match: 1 if same category, 0 otherwise
        category_matrix = pd.get_dummies(df_items.set_index('id')['category'])
        category_matrix = category_matrix.reindex(all_menu_ids).fillna(0)
        
        content_sim_matrix = cosine_similarity(category_matrix)
        content_sim_df = pd.DataFrame(content_sim_matrix, index=category_matrix.index, columns=category_matrix.index)
        
        # Build map for later reuse
        for item in items_data:
            item_category_map[item['id']] = item['category']
            
        print("Content-based model built.")
    else:
        content_sim_df = pd.DataFrame(0, index=all_menu_ids, columns=all_menu_ids)

    # --- Category-Level Collaborative Filtering ---
    # Goal: If users who buy Category A also buy Category B, then Items in A are similar to Items in B.
    # 1. Build User-Category Matrix
    cat_collab_sim_df = None
    
    if interactions_data and not df_items.empty:
        # Merge interactions with item data to get Category for each interaction
        df_interactions = pd.DataFrame(interactions_data)
        df_merged = df_interactions.merge(df_items, left_on='menu_id', right_on='id')
        
        # Pivot: User x Category (Sum of quantities)
        user_cat_matrix = df_merged.pivot_table(index='user_id', columns='category', values='quantity', aggfunc='sum').fillna(0)
        
        # Category-Category Similarity
        cat_user_matrix = user_cat_matrix.T
        cat_sim_matrix = cosine_similarity(cat_user_matrix)
        cat_sim_df = pd.DataFrame(cat_sim_matrix, index=cat_user_matrix.index, columns=cat_user_matrix.index)
        
        # Map back to Item-Item Matrix
        # For each pair of items (i, j), similarity = CatSim(Cat(i), Cat(j))
        # We can construct this by expanding the Category Similarity Matrix
        # A more efficient way: Create a matrix C (Items x Categories) (One-Hot)
        # Item_Cat_Sim = C * Cat_Sim * C.T
        
        C = pd.get_dummies(df_items.set_index('id')['category'])
        C = C.reindex(all_menu_ids).fillna(0)
        
        # Align columns of C with cat_sim_df index
        C = C.reindex(columns=cat_sim_df.index).fillna(0)
        
        # Dot product expansion
        # sim(i, j) = sum_over_cat_k_l ( IsCat(i, k) * IsCat(j, l) * Sim(k, l) )
        # Since IsCat(i, k) is 1 only if i is in k, this reduces to Sim(Cat(i), Cat(j))
        
        # Matrix multiplication: (N_items x N_cats) * (N_cats x N_cats) * (N_cats x N_items)
        # This gives N_items x N_items
        item_cat_collab_sim_matrix = C.dot(cat_sim_df).dot(C.T)
        
        cat_collab_sim_df = item_cat_collab_sim_matrix
        print("Category Collaborative model built.")
    else:
        cat_collab_sim_df = pd.DataFrame(0, index=all_menu_ids, columns=all_menu_ids)

    # --- Hybrid Model (Weighted Combination) ---
    # Weights for blending
    # W1 = Item Collaborative (User bought X and Y)
    # W2 = Content Based (X and Y are same category)
    # W3 = Category Collaborative (User bought Category(X) and Category(Y))
    
    W1 = 0.3 
    W2 = 0.5
    W3 = 0.2
    
    if not interactions_data:
        # Cold Start: Content Only
        W1, W2, W3 = 0.0, 1.0, 0.0
        print("Using Content-Only mode (Cold Start).")

    # Ensure indices align
    final_sim_df = (W1 * collab_sim_df) + (W2 * content_sim_df) + (W3 * cat_collab_sim_df)
    
    # Save model
    print(f"Saving hybrid model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(final_sim_df, f)
        
    print("Training complete.")

if __name__ == "__main__":
    train_model()
