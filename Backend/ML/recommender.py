
import os
import pickle
import sys
# Add parent directory to path to import db.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db import get_db_connection
except ImportError:
    # Fallback if running from proper context or failure
    from db import get_db_connection

class Recommender:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'recommendation_model.pkl')
        self.similarity_df = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.similarity_df = pickle.load(f)
                print("Recommendation model loaded.")
            else:
                print("Recommendation model not found. Training needed.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def get_top_n(self, user_id, n=5):
        if self.similarity_df is None:
            return []

        conn = None
        try:
            # Get user's purchase history
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT menu_id, SUM(quantity) as quantity
                FROM Orders o
                JOIN Order_Items oi ON o.id = oi.order_id
                WHERE o.user_id = %s
                GROUP BY menu_id
            """, (user_id,))
            user_items = cursor.fetchall()
            
            if not user_items:
                return []

            # Tally scores
            # Score = Sum(Similarity(Item_i, Candidate_j) * Qty_i)
            scores = {}
            user_purchased_ids = {item['menu_id'] for item in user_items}

            for item in user_items:
                menu_id = item['menu_id']
                qty = item['quantity']
                
                # Check if this menu_id exists in our model (it might be new)
                if menu_id in self.similarity_df.index:
                    similar_items = self.similarity_df[menu_id]
                    
                    for sim_id, score in similar_items.items():
                        # Optional: Don't recommend items user has already bought?
                        # For food, re-ordering is common, so we MIGHT want to include them.
                        # But prompt implies "suggestions" - usually new things or favorites.
                        # Let's simple include everything but boost un-bought?
                        # Or just standard score.
                        
                        if sim_id == menu_id: continue 
                        
                        if sim_id not in scores:
                            scores[sim_id] = 0
                        scores[sim_id] += score * qty

            # Sort by score
            sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top N IDs
            return [item[0] for item in sorted_items[:n]]
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close() # Cursor closes automatically or we assume
                except:
                    pass

# Singleton instance
recommender = Recommender()
