# 🍕 QuickBite — Food Delivery Application

> A full-stack food delivery web application built with Python + Flask as part of the UCT Full Stack Development Internship.

---

## 📌 Project Overview

QuickBite is a web-based food delivery platform that acts as a bridge between restaurants and customers. It allows restaurants to list their menu, customers to browse and order food, delivery drivers to accept and deliver orders, and admins to manage the entire platform.

This project was built over 4 weeks as part of the UCT internship program.

---

## 🚀 Live Features

- Customers can browse restaurants, view menus, add to cart, and place orders
- Restaurant owners can manage their menu and update order status
- Delivery drivers get notified of new orders and can accept/deliver them
- Live driver location tracking using OpenStreetMap
- Real-time popup notifications for all users
- Ratings and reviews after delivery
- Admin panel to manage users, restaurants, and view analytics

---

## 🏗️ Tech Stack

Backend       — Python 3.11 + Flask
Database      — SQLite via Flask-SQLAlchemy
Authentication — Flask-Login + Flask-Bcrypt
Frontend      — HTML5 + Bootstrap 5 + Jinja2
Map Tracking  — Leaflet.js + OpenStreetMap
Icons         — Font Awesome 6

---

## 📁 Project Structure

proproject/
│
├── app.py              → Main app, creates Flask app, seeds database
├── extensions.py       → db, bcrypt, login_manager instances
├── models.py           → All database models
├── requirements.txt    → Python dependencies
│
├── routes/
│   ├── auth.py         → Login, Register, Logout
│   ├── customer.py     → Home, Menu, Cart, Checkout, Tracking, Reviews
│   ├── restaurant.py   → Restaurant Dashboard, Menu Management
│   ├── driver.py       → Driver Dashboard, Accept/Pickup/Deliver orders
│   ├── admin.py        → Admin Panel — Users, Restaurants, Analytics
│   └── api.py          → API endpoints for notifications & order status
│
└── templates/
    ├── base.html        → Common navbar, footer, live notifications
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── customer/
    │   ├── home.html        → Restaurant listing with search & filters
    │   ├── menu.html        → Menu with recommendations & reviews
    │   ├── cart.html        → Shopping cart
    │   ├── checkout.html    → Checkout with address & payment
    │   ├── tracking.html    → Live order tracking with map
    │   ├── orders.html      → Order history
    │   └── notifications.html
    ├── restaurant/
    │   ├── dashboard.html   → Orders & revenue dashboard
    │   ├── menu.html        → Add/manage menu items
    │   └── setup.html       → New restaurant setup
    ├── driver/
    │   └── dashboard.html   → Available & active orders
    └── admin/
        ├── dashboard.html   → Platform stats
        ├── users.html       → All users
        └── restaurants.html → Manage restaurants

---

## 👥 User Roles

---

### 🛒 CUSTOMER

Login: Register a new account → select Customer

What they can do:
- Browse restaurants with search and cuisine filters
- View menus with Chef's Pick recommendations
- Add items to cart and place orders
- Save delivery addresses
- Track orders live on map
- Get real-time notifications
- Rate and review restaurants
- View order history

Order Flow:
1. Browse → Add to cart → Checkout
2. Enter address → Select payment → Place order
3. Status shows "Waiting for Driver"
4. Driver accepts → Track live on map
5. Order delivered → Leave review

---

### 🍕 RESTAURANT OWNER

Login:
Email    → owner@pizza.com
Password → owner123

What they can do:
- Set up restaurant profile
- Add/hide menu items with emoji, price, category
- Mark items as Chef's Pick
- View and manage all incoming orders
- Update order status step by step

Order Status Flow:
Pending → Confirmed → Preparing → Out for Delivery → Delivered

Note: When status is set to "Preparing", ALL available
drivers are notified. First driver to accept gets the order.

Default Restaurants:
- Pizza Palace   (Italian)   ⭐ 4.5
- Burger Barn    (American)  ⭐ 4.2
- Spice Garden   (Indian)    ⭐ 4.7

---

### 🛵 DELIVERY DRIVER

Login:
Email    → driver@food.com
Password → driver123

What they can do:
- See all available orders waiting for a driver
- Accept an order (first come first served)
- Mark order as Picked Up
- Mark order as Delivered
- View completed delivery history
- Dashboard auto-refreshes every 15 seconds

Order Flow for Driver:
1. New order appears in dashboard
2. Click "Accept This Order"
3. Go to restaurant → Click "Mark Picked Up"
4. Deliver to customer → Click "Mark Delivered"
5. Driver becomes free for next order

---

### 🧑‍💼 ADMIN

Login:
Email    → admin@food.com
Password → admin123

What they can do:
- View total users, restaurants, orders, revenue
- See all recent orders across all restaurants
- View all registered users
- Activate or deactivate any restaurant

---

## 🔄 Complete Order Flow

Customer places order
        ↓
Status: "Waiting for Driver"
All free drivers get notified
        ↓
First driver clicks Accept
Status: "Confirmed" — Customer notified
        ↓
Restaurant prepares food
Status: "Preparing"
        ↓
Driver picks up from restaurant
Status: "Out for Delivery"
Live map tracking activated
        ↓
Driver delivers to customer
Status: "Delivered"
        ↓
Customer rates the restaurant ⭐

---

## ⚙️ How to Run

Step 1 — Clone the repo
git clone https://github.com/YOUR_USERNAME/proproject.git
cd proproject

Step 2 — Install dependencies
pip install -r requirements.txt

Step 3 — Run the app
python app.py

Step 4 — Open browser
http://127.0.0.1:5000

---

## 🔐 Login Credentials

Admin       → admin@food.com    / admin123
Restaurant  → owner@pizza.com   / owner123
Driver      → driver@food.com   / driver123
Customer    → Register new account

---

## 📦 Dependencies

Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1

---

## 👩‍💻 Developer

Name        — Sudeshna Kalluri
Internship  — UCT Full Stack Development Internship
Project     — QuickBite Food Delivery Application
