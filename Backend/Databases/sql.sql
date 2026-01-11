
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

CREATE TABLE RestaurantRequests (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100)
);


CREATE TABLE Menu (
    id INT PRIMARY KEY,
    restaurant_id INT NOT NULL, 
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    availability BOOLEAN DEFAULT TRUE,
    category VARCHAR(50),
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

CREATE TABLE address (
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

-----HI git fay---

----INSERTS-------
INSERT INTO bongus (id, username, password_hash) VALUES
(1, 'Bongu', '$2b$12$wcD2F4fh2E0OXwsngUkDUeDEZN4Ei/VMf.jm0wEk15dS20cbVyQrS');

INSERT INTO restaurants (id, name, location, username, rating) VALUES
(1, 'The S Jail Hotel', 'Main Road, Toll Naka', 'sjailhotel', 3.9),
(2, 'KFC', 'Hosapur', 'kfc_official', 4.0),
(3, 'Disha Darshini', 'Sattur', 'dishadarshini', 4.3),
(4, 'Pizza Hut', 'Hosur Cross Road', '12345', .4.5),
(7, 'Sri Krishna Bhavan', 'P.B. Road', 'krishnabhavan', 4.1),
(8, 'Empire Restaurant', 'P.B. Road', 'empirerestaurant', 4.2),
(9, 'Green Park', 'P.B. Road', 'greenpark', 3.8),
(10, 'Domino''s Pizza', 'Vidyagiri', 'dominos', 4.4),
(11, 'Rasoi Veg Thali', 'Club Road', 'rasoiveg', 4.0),
(12, 'Hotel Naveen', 'Station Road', 'hotelnaveen', 3.7);

INSERT INTO restaurantrequests (id, name, location, contact, password_hash, username) VALUES
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


INSERT INTO menu (id, restaurant_id, item_name, price, availability) VALUES
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
-- Empire Restaurant (restaurant_id: 8)
(23, 8, 'Butter Chicken', 299.00, 1),
(24, 8, 'Veg Manchurian', 179.00, 1),
(25, 8, 'Chicken Biryani', 249.00, 1),
(26, 8, 'Naan Platter', 129.00, 0),
-- Green Park (restaurant_id: 9)
(27, 9, 'Pav Bhaji', 99.00, 1),
(28, 9, 'Chole Bhature', 149.00, 1),
(29, 9, 'Green Salad', 79.00, 1),
(30, 9, 'Masala Papad', 49.00, 0),
-- Domino's Pizza (restaurant_id: 10)
(31, 10, 'Farmhouse Pizza', 229.00, 1),
(32, 10, 'Chicken Dominator', 299.00, 1),
(33, 10, 'Garlic Breadsticks', 99.00, 1),
(34, 10, 'Taco Mexicana', 179.00, 0),
-- Rasoi Veg Thali (restaurant_id: 11)
(35, 11, 'Deluxe Veg Thali', 199.00, 1),
(36, 11, 'Mini Thali', 129.00, 1),
(37, 11, 'Sweet Lassi', 59.00, 1),
(38, 11, 'Gujarati Thali', 249.00, 0),
-- Hotel Naveen (restaurant_id: 12)
(39, 12, 'Chicken Curry', 179.00, 1),
(40, 12, 'Veg Pulao', 129.00, 1),
(41, 12, 'Roti Basket', 69.00, 1),
(42, 12, 'Fish Fry', 199.00, 0);

