from flask import Blueprint, jsonify
from db import cursor

menu = Blueprint('menu', __name__)

@menu.route('/menu/<int:restaurant_id>', methods=['GET'])
def get_menu(restaurant_id):
    cursor.execute("SELECT * FROM Menu WHERE restaurant_id = %s", (restaurant_id,))
    return jsonify(cursor.fetchall())
