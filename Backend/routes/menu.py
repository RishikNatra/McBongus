from flask import Blueprint, jsonify
import mysql.connector

menu_bp = Blueprint('menu_bp', __name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rishik@1429145",
    database="McBongus_DB"
)


