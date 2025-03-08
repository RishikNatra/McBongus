from flask import Flask, render_template
from routes.auth import auth
from routes.restaurant import restaurant
from routes.menu import menu

app = Flask(__name__)

# Register blueprints (modular routing)
app.register_blueprint(auth)
app.register_blueprint(restaurant)
app.register_blueprint(menu)
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
