from flask import Blueprint, jsonify
import mysql.connector
from db import get_db_connection

menu_bp = Blueprint('menu_bp', __name__)

# Database connection
db = get_db_connection()


