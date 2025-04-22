McBongus - Food Delivery Platform

McBongus is a web-based food delivery platform built with Flask and MySQL, allowing users to browse restaurants, place orders, and track deliveries. Restaurants can manage orders, and delivery partners (Bongus) can accept and update delivery statuses. This project includes a responsive frontend and a robust backend with user authentication, order management, and database integration.

Table of Contents
- Project Overview
- Prerequisites
- Setup Instructions
  - 1. Clone the Repository
  - 2. Set Up the Virtual Environment
  - 3. Configure the Database
  - 4. Run the Application
- Database Schema
- Directory Structure
- Troubleshooting
- Contributing
- License

Project Overview
McBongus provides a seamless food ordering experience with the following features:
- User Features: Browse restaurants, view menus, place orders, track orders, manage addresses.
- Restaurant Features: Register, log in, accept/reject orders, manage menus.
- Delivery Partner (Bongu) Features: Accept delivery requests, update delivery statuses.
- Admin Features: (Future scope) Manage restaurant requests and platform operations.

The backend is built with Flask, using MySQL for data storage. The frontend uses HTML, CSS, and JavaScript, with templates rendered via Jinja2.

Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.8+: Download from https://www.python.org/downloads/
- MySQL: Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
- Git: Download from https://git-scm.com/downloads
- pip: Python package manager (included with Python)
- A code editor like VS Code (optional but recommended)

Setup Instructions

1. Clone the Repository
Download the project from GitHub to your local machine.

Run: `git clone https://github.com/<your-username>/McBongus.git`
Then: `cd McBongus/Backend`

Replace `<your-username>` with your GitHub username or the correct repository URL.

2. Set Up the Virtual Environment
Create and activate a Python virtual environment to manage dependencies.

Run: `python -m venv venv`

Activate the virtual environment:
- On Windows: `.\venv\Scripts\activate`
- On macOS/Linux: `source venv/bin/activate`

Install the required Python packages listed in `requirements.txt`:
Run: `pip install -r requirements.txt`

Note: If `requirements.txt` is missing, install the following packages manually:
Run: `pip install flask flask-bcrypt flask-session mysql-connector-python`

3. Configure the Database
The project uses a MySQL database named `McBongus_DB`. Follow these steps to set it up.

Step 1: Update config.py
Modify the database configuration in `Backend/config.py` to match your MySQL settings.

1. Open `Backend/config.py` in a text editor.
2. Replace the default settings with your MySQL credentials:
   # config.py
   DB_CONFIG = {
       "host": "localhost",
       "user": "your_mysql_username",  # e.g., "root"
       "password": "your_mysql_password",  # Your MySQL password
       "database": "McBongus_DB",
       "port": 3306
   }
3. Save the file.

Step 2: Set Up the Database
Create the `McBongus_DB` database and tables by running the provided SQL commands in your MySQL client (e.g., MySQL Workbench, phpMyAdmin, or the MySQL command line).

1. Open your MySQL client and log in:
   Run: `mysql -u your_mysql_username -p`
   Enter your MySQL password when prompted.

2. Run the following SQL commands to create the database, tables, and insert initial data:

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
   INSERT
