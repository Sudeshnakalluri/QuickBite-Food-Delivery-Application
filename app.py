from extensions import db, bcrypt, login_manager
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_delivery.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from routes.auth import auth
    from routes.api import api
    from routes.customer import customer
    from routes.restaurant import restaurant
    from routes.admin import admin
    from routes.driver import driver

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(customer)
    app.register_blueprint(restaurant)
    app.register_blueprint(admin)
    app.register_blueprint(driver)

    return app

app = create_app()

with app.app_context():
    db.create_all()
    from models import User, Restaurant, MenuItem

    if not User.query.first():
        admin_user = User(name='Admin', email='admin@food.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'), role='admin')
        db.session.add(admin_user)

        owner = User(name='Restaurant Owner', email='owner@pizza.com',
            password=bcrypt.generate_password_hash('owner123').decode('utf-8'), role='restaurant')
        db.session.add(owner)

        driver1 = User(name='Rajan Kumar', email='driver@food.com',
            password=bcrypt.generate_password_hash('driver123').decode('utf-8'), role='driver',
            driver_lat=19.0820, driver_lng=72.8900)
        db.session.add(driver1)
        db.session.flush()

        r1 = Restaurant(name='Pizza Palace', cuisine='Italian', owner_id=owner.id,
                        address='123 Main St, Mumbai', rating=4.5, delivery_time=30,
                        lat=19.0760, lng=72.8777)
        r2 = Restaurant(name='Burger Barn', cuisine='American', owner_id=owner.id,
                        address='456 Oak Ave, Mumbai', rating=4.2, delivery_time=25,
                        lat=19.0800, lng=72.8850)
        r3 = Restaurant(name='Spice Garden', cuisine='Indian', owner_id=owner.id,
                        address='789 Curry Lane, Mumbai', rating=4.7, delivery_time=40,
                        lat=19.0700, lng=72.8700)
        db.session.add_all([r1, r2, r3])
        db.session.flush()

        items = [
            MenuItem(name='Margherita Pizza', price=299, restaurant_id=r1.id, category='Pizza',
                     description='Classic tomato & cheese', emoji='🍕', is_recommended=True),
            MenuItem(name='Pepperoni Pizza', price=399, restaurant_id=r1.id, category='Pizza',
                     description='Loaded with pepperoni', emoji='🍕'),
            MenuItem(name='Garlic Bread', price=99, restaurant_id=r1.id, category='Sides',
                     description='Crispy garlic bread', emoji='🥖'),
            MenuItem(name='Classic Burger', price=199, restaurant_id=r2.id, category='Burgers',
                     description='Juicy beef patty', emoji='🍔', is_recommended=True),
            MenuItem(name='Cheese Burger', price=249, restaurant_id=r2.id, category='Burgers',
                     description='Double cheese loaded', emoji='🍔'),
            MenuItem(name='Fries', price=99, restaurant_id=r2.id, category='Sides',
                     description='Crispy golden fries', emoji='🍟'),
            MenuItem(name='Butter Chicken', price=349, restaurant_id=r3.id, category='Curries',
                     description='Rich creamy curry', emoji='🍛', is_recommended=True),
            MenuItem(name='Dal Makhani', price=249, restaurant_id=r3.id, category='Curries',
                     description='Slow cooked lentils', emoji='🫕'),
            MenuItem(name='Naan', price=49, restaurant_id=r3.id, category='Breads',
                     description='Fresh tandoor naan', emoji='🫓'),
        ]
        db.session.add_all(items)
        db.session.commit()
        print("✅ Database seeded successfully!")
    else:
        print("✅ Database already exists, skipping seed.")

if __name__ == '__main__':
    print("🍕 Starting QuickBite Food Delivery App...")
    print("🌐 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
