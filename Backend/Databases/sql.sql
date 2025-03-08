CREATE DATABASE McBongus_DB;
USE McBongus_DB;

-- Users Table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin', 'restaurant_owner', 'delivery_partner') NOT NULL
);

-- Restaurants Table
CREATE TABLE Restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Menu Table
CREATE TABLE Menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    status ENUM('pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'pending',
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(id) ON DELETE CASCADE
);

-- Order Items Table (Many-to-Many Relationship between Orders & Menu)
CREATE TABLE Order_Items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menu(id) ON DELETE CASCADE
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

-- Use the database
USE McBongus_DB;

-- Insert Users (Customers, Admin, Restaurant Owners, Delivery Partners)
INSERT INTO Users (name, email, password, role) VALUES
('John Doe', 'john@example.com', 'hashedpassword1', 'customer'),
('Jane Smith', 'jane@example.com', 'hashedpassword2', 'customer'),
('Admin User', 'admin@example.com', 'adminpassword', 'admin'),
('Resto Owner', 'owner@example.com', 'ownerpassword', 'restaurant_owner'),
('Delivery Guy', 'delivery@example.com', 'deliverypassword', 'delivery_partner');

-- Insert Restaurants
INSERT INTO Restaurants (name, location, owner_id) VALUES
('Bongu’s Pizza', '123 College Street', 4),
('Burger Land', '456 University Road', 4);

-- Insert Menu Items
INSERT INTO Menu (restaurant_id, item_name, price, availability) VALUES
(1, 'Margherita Pizza', 8.99, TRUE),
(1, 'Pepperoni Pizza', 10.99, TRUE),
(1, 'Veggie Pizza', 9.49, TRUE),
(2, 'Classic Burger', 5.99, TRUE),
(2, 'Cheese Burger', 6.99, TRUE),
(2, 'Chicken Burger', 7.99, TRUE);

-- Insert Orders
INSERT INTO Orders (user_id, restaurant_id, status, total_price) VALUES
(1, 1, 'pending', 19.98),
(2, 2, 'confirmed', 12.99);

-- Insert Order Items (Linking Orders & Menu)
INSERT INTO Order_Items (order_id, menu_id, quantity, price) VALUES
(1, 1, 2, 17.98),
(2, 4, 2, 11.98);

-- Insert Payments
INSERT INTO Payments (order_id, payment_status, transaction_id) VALUES
(1, 'completed', 'TXN123456'),
(2, 'pending', 'TXN789101');

-- Insert Delivery Assignments
INSERT INTO Delivery (order_id, delivery_status, driver_id, delivery_time) VALUES
(1, 'out_for_delivery', 5, NOW()),
(2, 'pending', NULL, NULL);
