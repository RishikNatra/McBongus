
from flask import Blueprint, jsonify, session
from db import get_db_connection
import sys
import os

# Ensure ML package is reachable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ML.recommender import recommender
except ImportError:
    # Fallback or handle error
    print("Warning: Could not import recommender")
    recommender = None

recommendations_bp = Blueprint('recommendations_bp', __name__)

@recommendations_bp.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    user_id = session.get('user_id')
    
    recommended_items = []
    
    if user_id and recommender:
        try:
            # Get ML recommendations
            menu_ids = recommender.get_top_n(user_id, n=4)
            
            if menu_ids:
                # Fetch details
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                # MySQL IN clause needs formatting
                format_strings = ','.join(['%s'] * len(menu_ids))
                cursor.execute(f"SELECT * FROM Menu WHERE id IN ({format_strings})", tuple(menu_ids))
                recommended_items = cursor.fetchall()
                # Sort them in the order of menu_ids (relevance) instead of ID
                # Create a map for sorting
                item_map = {item['id']: item for item in recommended_items}
                recommended_items = [item_map[mid] for mid in menu_ids if mid in item_map]
                
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    
    # Fallback: If no user or no recommendations, return Popular items
    if not recommended_items:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Top 4 most ordered items
            cursor.execute("""
                SELECT m.*, SUM(oi.quantity) as popularity 
                FROM Menu m
                JOIN Order_Items oi ON m.id = oi.menu_id
                GROUP BY m.id
                ORDER BY popularity DESC
                LIMIT 4
            """)
            recommended_items = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error getting popular items: {e}")

    return jsonify(recommended_items)
