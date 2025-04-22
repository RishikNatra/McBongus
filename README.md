# McBongus
McBongus - Food Delivery Platform
McBongus is a web-based food delivery platform built with Flask and MySQL, allowing users to browse restaurants, place orders, and track deliveries. Restaurants can manage orders, and delivery partners (Bongus) can accept and update delivery statuses. This project includes a responsive frontend and a robust backend with user authentication, order management, and database integration.
Table of Contents
Project Overview (#project-overview)

Prerequisites (#prerequisites)

Setup Instructions (#setup-instructions)
1. Clone the Repository (#1-clone-the-repository)

2. Set Up the Virtual Environment (#2-set-up-the-virtual-environment)

3. Configure the Database (#3-configure-the-database)

4. Run the Application (#4-run-the-application)

Database Schema (#database-schema)

Directory Structure (#directory-structure)

Troubleshooting (#troubleshooting)

Contributing (#contributing)

License (#license)

Project Overview
McBongus provides a seamless food ordering experience with the following features:
User Features: Browse restaurants, view menus, place orders, track orders, manage addresses.

Restaurant Features: Register, log in, accept/reject orders, manage menus.

Delivery Partner (Bongu) Features: Accept delivery requests, update delivery statuses.

Admin Features: (Future scope) Manage restaurant requests and platform operations.

The backend is built with Flask, using MySQL for data storage. The frontend uses HTML, CSS, and JavaScript, with templates rendered via Jinja2.
Prerequisites
Before setting up the project, ensure you have the following installed:
Python 3.8+: Download Python

MySQL: Download MySQL Community Server

Git: Download Git

pip: Python package manager (included with Python)

A code editor like VS Code (optional but recommended)

Setup Instructions
1. Clone the Repository
Download the project from GitHub to your local machine.
bash

git clone https://github.com/<your-username>/McBongus.git
cd McBongus/Backend

Replace <your-username> with your GitHub username or the correct repository URL.
2. Set Up the Virtual Environment
Create and activate a Python virtual environment to manage dependencies.
bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Install the required Python packages listed in requirements.txt:
bash

pip install -r requirements.txt

Note: If requirements.txt is missing, install the following packages manually:
bash

pip install flask flask-bcrypt flask-session mysql-connector-python

3. Configure the Database
The project uses a MySQL database named McBongus_DB. Follow these steps to set it up.
Step 1: Update config.py
Modify the database configuration in Backend/config.py to match your MySQL settings.
Open Backend/config.py in a text editor.

Replace the default settings with your MySQL credentials:
python

# config.py
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_username",  # e.g., "root"
    "password": "your_mysql_password",  # Your MySQL password
    "database": "McBongus_DB",
    "port": 3306
}

Save the file.

Step 2: Set Up the Database
Create the McBongus_DB database and tables by running the provided SQL commands in your MySQL client (e.g., MySQL Workbench, phpMyAdmin, or the MySQL command line).
Open your MySQL client and log in:
bash

mysql -u your_mysql_username -p

Enter your MySQL password when prompted.

Run the following SQL commands to create the database and tables, and insert initial data:
sql

CREATE DATABASE McBongus_DB;
USE McBongus_DB;

-- Users Table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin', 'restaurant_owner', 'delivery_partner') NOT NULL
);

-- Bongus Table (Delivery Partners)
CREATE TABLE Bongus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Restaurants Table
CREATE TABLE Restaurants (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    rating DECIMAL(2,1)
);

-- Restaurant Requests Table
CREATE TABLE RestaurantRequests (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100)
);

-- Menu Table
CREATE TABLE Menu (
    id INT PRIMARY KEY,
    restaurant_id INT NOT NULL, 
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    availability BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(id) ON DELETE CASCADE
);

-- Orders Table
CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    status ENUM(
        'pending',
        'restaurant_accepted',
        'canceled_awaiting_refund',
        'bongu_accepted',
        'preparing',
        'out_for_delivery',
        'delivered',
        'canceled'
    ) DEFAULT 'pending',
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bongu_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(id) ON DELETE CASCADE,
    FOREIGN KEY (bongu_id) REFERENCES Bongus(id) ON DELETE SET NULL
);

-- Order Items Table
CREATE TABLE Order_Items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menu(id) ON DELETE CASCADE
);

-- Address Table
CREATE TABLE Address (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    apartment_no VARCHAR(20),
    apartment_name VARCHAR(100),
    landmark VARCHAR(255),
    road_no VARCHAR(50),
    locality VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    PRIMARY KEY (id),
    KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE Payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    transaction_id VARCHAR(255) UNIQUE,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE
);

-- Delivery Table
CREATE TABLE Delivery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    delivery_status ENUM('pending', 'assigned', 'out_for_delivery', 'delivered', 'failed') DEFAULT 'pending',
    driver_id INT,
    delivery_time TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES Users(id) ON DELETE SET NULL
);

-- Insert Initial Data
INSERT INTO Bongus (id, username, password_hash) VALUES
(1, 'Bongu', '$2b$12$wcD2F4fh2E0OXwsngUkDUeDEZN4Ei/VMf.jm0wEk15dS20cbVyQrS');

INSERT INTO Restaurants (id, name, location, username, rating) VALUES
(1, 'The S Jail Hotel', 'Main Road, Toll Naka', 'sjailhotel', 3.9),
(2, 'KFC', 'Hosapur', 'kfc_official', 4.0),
(3, 'Disha Darshini', 'Sattur', 'dishadarshini', 4.3),
(4, 'Pizza Hut', 'Hosur Cross Road', '12345', 4.5),
(7, 'Sri Krishna Bhavan', 'P.B. Road', 'krishnabhavan', 4.1),
(8, 'Empire Restaurant', 'P.B. Road', 'empirerestaurant', 4.2),
(9, 'Green Park', 'P.B. Road', 'greenpark', 3.8),
(10, 'Domino''s Pizza', 'Vidyagiri', 'dominos', 4.4),
(11, 'Rasoi Veg Thali', 'Club Road', 'rasoiveg', 4.0),
(12, 'Hotel Naveen', 'Station Road', 'hotelnaveen', 3.7);

INSERT INTO RestaurantRequests (id, name, location, contact, password_hash, username) VALUES
(1, 'The S Jail Hotel', '12th Avenue, Bangalore', 'sjail_contact', '$2b$12$XZYBZmYZSzltsL25hHI8EOKiGhax9afD4.1EwqXMpVh7E2ejDXSty', 'sjailhotel'),
(2, 'KFC', 'Multiple Locations', 'kfc_contact', '$2b$12$cdq9ojwZ8WIlEYUs0ZV0PefUr8ilD3CfK7psuyX3AnL2zTnpp9Gz6', 'kfc_official'),
(3, 'Disha Darshini', 'Koramangala, Bangalore', 'disha_contact', '$2b$12$.xaRrF16tmOYio5Ermc3aebjliRIj23AAKFH6.xqOvnwQ5oJU7JNy', 'dishadarshini'),
(4, 'Pizza Hut', 'Dharwad', '12345', '$2b$12$XRlQhyTX8bJI3NSahqhCK.ViN5HujAo5CLIVA8mtvMF3o.XHuWts6', '12345'),
(7, 'Sri Krishna Bhavan', 'P.B. Road', '5', '$2b$12$30NETjVQE.iXHScu6UbWmuUOIkqZYAsgNUosmS5uvFrnymBs5OsUS', 'krishnabhavan'),
(8, 'Empire Restaurant', 'P.B. Road', '6', '$2b$12$wEj8.oswNeGWZH5OAvIJsu9CzfkWe6KeDLxlyBF0QyQZh0tdZKA9e', 'empirerestaurant'),
(9, 'Green Park', 'P.B. Road', 'Nehru Nagar', '$2b$12$r/Muw2xMbvA5VhborlUc3OQAkguCk8j0cR2cR6pmwVziGogoFBXn6', 'greenpark'),
(10, 'Domino''s Pizza', 'Vidyagiri', '8', '$2b$12$toGH1pEvoSTBHODpZZNXaeNRnetDfy70ZVmdiknzBQyU6lNtkX6Xq', 'dominos'),
(11, 'Rasoi Veg Thali', 'Club Road', '9', '$2b$12$v6AIohTsdcVsElVrPBdWB.MGj/uaQ8QEyDQQzJMEMkJ2t9d0ISi5e', 'rasoiveg'),
(12, 'Hotel Naveen', 'Station Road', '10', '$2b$12$Zc9/LApyuz.OWSAOEljN6.v718fszlioDQzWTp5kKCopyNr1L9fm.', 'hotelnaveen');

INSERT INTO Menu (id, restaurant_id, item_name, price, availability) VALUES
(1, 1, 'Prison Special Biryani', 199.00, 1),
(2, 1, 'Jail Tandoori Platter', 299.00, 1),
(3, 1, 'Handcuff Paneer Tikka', 249.00, 0),
(4, 2, 'Zinger Burger', 149.00, 1),
(5, 2, 'Hot Wings (6 pcs)', 199.00, 1),
(6, 2, 'Chicken Bucket', 599.00, 1),
(7, 3, 'Masala Dosa', 80.00, 1),
(8, 3, 'Idli Vada Combo', 60.00, 1),
(9, 3, 'Filter Coffee', 30.00, 1),
(10, 1, 'Chicken 65', 249.00, 1),
(11, 1, 'Paneer Chilli', 199.00, 1),
(12, 4, 'Margherita Pizza', 199.00, 1),
(13, 4, 'Pepperoni Pizza', 249.00, 1),
(14, 4, 'Veggie Supreme Pizza', 229.00, 1),
(15, 4, 'BBQ Chicken Pizza', 279.00, 1),
(16, 4, 'Cheese Burst Pizza', 249.00, 1),
(17, 4, 'Paneer Tikka Pizza', 239.00, 1),
(18, 4, 'Hawaiian Pizza', 259.00, 0),
(19, 7, 'Plain Dosa', 70.00, 1),
(20, 7, 'Ghee Roast Dosa', 120.00, 1),
(21, 7, 'Rava Idli', 60.00, 1),
(22, 7, 'Mysore Masala Dosa', 100.00, 0),
(23, 8, 'Butter Chicken', 299.00, 1),
(24, 8, 'Veg Manchurian', 179.00, 1),
(25, 8, 'Chicken Biryani', 249.00, 1),
(26, 8, 'Naan Platter', 129.00, 0),
(27, 9, 'Pav Bhaji', 99.00, 1),
(28, 9, 'Chole Bhature', 149.00, 1),
(29, 9, 'Green Salad', 79.00, 1),
(30, 9, 'Masala Papad', 49.00, 0),
(31, 10, 'Farmhouse Pizza', 229.00, 1),
(32, 10, 'Chicken Dominator', 299.00, 1),
(33, 10, 'Garlic Breadsticks', 99.00, 1),
(34, 10, 'Taco Mexicana', 179.00, 0),
(35, 11, 'Deluxe Veg Thali', 199.00, 1),
(36, 11, 'Mini Thali', 129.00, 1),
(37, 11, 'Sweet Lassi', 59.00, 1),
(38, 11, 'Gujarati Thali', 249.00, 0),
(39, 12, 'Chicken Curry', 179.00, 1),
(40, 12, 'Veg Pulao', 129.00, 1),
(41, 12, 'Roti Basket', 69.00, 1),
(42, 12, 'Fish Fry', 199.00, 0);

Alternatively, if you have the sql.sql file in your project:
Import it into MySQL:
bash

mysql -u your_mysql_username -p McBongus_DB < sql.sql

This executes all the SQL commands in sql.sql to create the database, tables, and insert initial data.

4. Run the Application
Start the Flask application to run McBongus locally.
bash

# Ensure you're in the Backend directory
cd Backend

# Activate the virtual environment (if not already activated)
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux

# Run the Flask app
python app.py

Open a web browser and navigate to http://localhost:5000 to access the McBongus homepage.

Test features like user login (/user-login), restaurant login (/restaurant-login), and Bongu login (/bongu-login).

Database Schema
The McBongus_DB database consists of the following tables:
Users: Stores customer and admin information.

Bongus: Stores delivery partner (Bongu) credentials.

Restaurants: Stores approved restaurant details.

RestaurantRequests: Stores pending restaurant registration requests.

Menu: Stores menu items for each restaurant.

Orders: Tracks orders with statuses (e.g., pending, delivered).

Order_Items: Links orders to menu items with quantities.

Address: Stores user delivery addresses.

Payments: Tracks payment status for orders.

Delivery: Tracks delivery status and driver assignments.

The SQL commands above create these tables with appropriate constraints and insert initial data for testing.
Directory Structure

McBongus/
├── Backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Database configuration
│   ├── db.py               # Database connection logic
│   ├── sql.sql             # SQL schema and initial data
│   ├── requirements.txt    # Python dependencies
│   ├── routes/
│   │   ├── auth.py         # User authentication routes
│   │   ├── bongu.py        # Delivery partner routes
│   │   ├── restaurant.py   # Restaurant routes
│   │   ├── menu.py         # Menu routes (optional)
│   ├── static/
│   │   ├── images/         # Category and restaurant images
│   │   ├── styles-home.css # Homepage styling
│   │   ├── styles-main.css # Main page styling
│   ├── templates/
│   │   ├── index.html      # Homepage template
│   │   ├── main.html       # Restaurants page template
│   │   ├── user-login.html # User login template
│   │   ├── bongu-login.html # Bongu login template
│   │   ├── restaurant-login.html # Restaurant login template
│   │   ├── ...             # Other HTML templates
│   ├── venv/               # Virtual environment
├── .gitignore              # Git ignore file
├── README.md               # This file

Troubleshooting
MySQL Connection Error:
Ensure MySQL is running and credentials in config.py are correct.

Verify the McBongus_DB database exists and tables are created.

Missing Dependencies:
If pip install -r requirements.txt fails, install packages manually (see Step 2).

Template Not Found:
Ensure all HTML files are in Backend/templates/.

Image Not Loading:
Verify image files (e.g., burger.png, kfc.jpg) exist in Backend/static/images/.

Port Conflict:
If localhost:5000 is in use, change the port in app.py:
python

if __name__ == '__main__':
    app.run(debug=True, port=5001)

