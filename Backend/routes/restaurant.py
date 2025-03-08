from flask import Blueprint, jsonify
from db import cursor

restaurant = Blueprint('restaurant', __name__)

@restaurant.route('/restaurants', methods=['GET'])
def get_restaurants():
    cursor.execute("SELECT * FROM Restaurants")
    return jsonify(cursor.fetchall())
