import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rishik@1429145",
    "database": "mcbongus_db",
    "port": 3306
}

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()
