
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
            # Get user's purchase history WITH CATEGORY
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT oi.menu_id, SUM(oi.quantity) as quantity, m.category
                FROM Orders o
                JOIN Order_Items oi ON o.id = oi.order_id
                JOIN Menu m ON oi.menu_id = m.id
                WHERE o.user_id = %s
                GROUP BY oi.menu_id, m.category
            """, (user_id,))
            user_items = cursor.fetchall()
            
            if not user_items:
                return []

            # Calculate Category Preferences
            # Format: {'Pizza': 10, 'Burgers': 2, ...}
            category_counts = {}
            total_qty = 0
            user_purchased_ids = set()
            
            for item in user_items:
                cat = item['category']
                qty = float(item['quantity'])
                category_counts[cat] = category_counts.get(cat, 0) + qty
                total_qty += qty
                user_purchased_ids.add(item['menu_id'])

            # Normalize to get weights (0 to 1)
            # e.g. Pizza: 0.8, Burgers: 0.2
            category_weights = {k: v / total_qty for k, v in category_counts.items()}
            
            # Fetch ALL item categories for lookup
            # Map: item_id -> category
            cursor.execute("SELECT id, category FROM Menu")
            all_items = cursor.fetchall()
            item_category_map = {item['id']: item['category'] for item in all_items}

            # Tally scores
            # Score = Sum(Similarity(Item_i, Candidate_j) * Qty_i)
            # BOOST: FinalScore = Score * (1 + BOOST_FACTOR * CategoryWeight(Category_j))
            scores = {}

            for item in user_items:
                menu_id = item['menu_id']
                qty = float(item['quantity'])
                
                # Check if this menu_id exists in our model (it might be new)
                if menu_id in self.similarity_df.index:
                    similar_items = self.similarity_df[menu_id]
                    
                    for sim_id, score in similar_items.items():
                        if sim_id == menu_id: continue 
                        
                        if sim_id not in scores:
                            scores[sim_id] = 0
                        scores[sim_id] += score * qty

            # Apply Category Boost
            # This ensures items in user's favorite categories float to the top
            BOOST_FACTOR = 2.0 # Significant boost
            
            final_scores = {}
            for item_id, raw_score in scores.items():
                cat = item_category_map.get(item_id)
                boost = 1.0
                if cat and cat in category_weights:
                    # e.g. 1 + 2.0 * 0.8 = 2.6x multiplier for Pizza items
                    boost = 1.0 + (BOOST_FACTOR * category_weights[cat])
                
                final_scores[item_id] = raw_score * boost

            # Sort by score
            sorted_items = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
            
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
