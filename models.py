from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='customer')  # customer, restaurant, admin, driver
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    driver_lat = db.Column(db.Float, default=19.0760)
    driver_lng = db.Column(db.Float, default=72.8777)
    orders = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.user_id')
    deliveries = db.relationship('Order', backref='driver', lazy=True, foreign_keys='Order.driver_id')

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(50))
    address = db.Column(db.String(200))
    rating = db.Column(db.Float, default=4.0)
    total_ratings = db.Column(db.Integer, default=0)
    delivery_time = db.Column(db.Integer, default=30)
    image = db.Column(db.String(100), default='default.jpg')
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lat = db.Column(db.Float, default=19.0760)
    lng = db.Column(db.Float, default=72.8777)
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)
    orders = db.relationship('Order', backref='restaurant', lazy=True)
    reviews = db.relationship('Review', backref='restaurant', lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    emoji = db.Column(db.String(10), default='🍽️')
    is_available = db.Column(db.Boolean, default=True)
    is_recommended = db.Column(db.Boolean, default=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Pending')
    delivery_address = db.Column(db.String(300))
    payment_method = db.Column(db.String(30), default='Cash on Delivery')
    payment_status = db.Column(db.String(20), default='Pending')
    eta_minutes = db.Column(db.Integer, default=30)
    special_instructions = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    review = db.relationship('Review', backref='order', lazy=True, uselist=False)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='reviews')

class SavedAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    label = db.Column(db.String(50))
    address = db.Column(db.String(300))
    user = db.relationship('User', backref='saved_addresses')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(300))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='notifications')
