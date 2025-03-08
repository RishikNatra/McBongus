from db import cursor, db

def get_user_by_username(username):
    cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
    return cursor.fetchone()

def create_user(username, hashed_password):
    cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
    db.commit()
