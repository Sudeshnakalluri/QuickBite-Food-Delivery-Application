from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Restaurant, MenuItem, Order, Notification, User

restaurant = Blueprint('restaurant', __name__, url_prefix='/restaurant')

def restaurant_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ['restaurant', 'admin']:
            flash('Access denied!', 'danger')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated

@restaurant.route('/dashboard')
@login_required
@restaurant_required
def dashboard():
    my_restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not my_restaurant:
        return render_template('restaurant/setup.html')
    orders = Order.query.filter_by(restaurant_id=my_restaurant.id).order_by(Order.created_at.desc()).limit(15).all()
    total_revenue = sum(o.total_amount for o in Order.query.filter_by(restaurant_id=my_restaurant.id).all())
    pending_count = Order.query.filter_by(restaurant_id=my_restaurant.id, status='Pending').count()
    return render_template('restaurant/dashboard.html', restaurant=my_restaurant,
                           orders=orders, total_revenue=total_revenue, pending_count=pending_count)

@restaurant.route('/setup', methods=['GET', 'POST'])
@login_required
@restaurant_required
def setup():
    if request.method == 'POST':
        r = Restaurant(name=request.form.get('name'), cuisine=request.form.get('cuisine'),
                       address=request.form.get('address'),
                       delivery_time=request.form.get('delivery_time', 30), owner_id=current_user.id)
        db.session.add(r)
        db.session.commit()
        flash('Restaurant created!', 'success')
        return redirect(url_for('restaurant.dashboard'))
    return render_template('restaurant/setup.html')

@restaurant.route('/menu')
@login_required
@restaurant_required
def menu():
    my_restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    items = MenuItem.query.filter_by(restaurant_id=my_restaurant.id).all() if my_restaurant else []
    return render_template('restaurant/menu.html', restaurant=my_restaurant, items=items)

@restaurant.route('/menu/add', methods=['POST'])
@login_required
@restaurant_required
def add_item():
    my_restaurant = Restaurant.query.filter_by(owner_id=current_user.id).first()
    item = MenuItem(name=request.form.get('name'), description=request.form.get('description'),
                    price=float(request.form.get('price')), category=request.form.get('category'),
                    emoji=request.form.get('emoji', '🍽️'),
                    is_recommended='recommended' in request.form,
                    restaurant_id=my_restaurant.id)
    db.session.add(item)
    db.session.commit()
    flash('Menu item added!', 'success')
    return redirect(url_for('restaurant.menu'))

@restaurant.route('/menu/toggle/<int:item_id>')
@login_required
@restaurant_required
def toggle_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    return redirect(url_for('restaurant.menu'))

@restaurant.route('/order/<int:order_id>/update', methods=['POST'])
@login_required
@restaurant_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    order.status = new_status

    # When restaurant starts preparing — notify ALL free drivers
    if new_status == 'Preparing':
        free_drivers = User.query.filter_by(role='driver', is_available=True).all()
        for drv in free_drivers:
            n = Notification(user_id=drv.id,
                message=f'🛵 New order #{order.id} ready for pickup at {order.restaurant.name}! First to accept gets it.')
            db.session.add(n)

    db.session.commit()

    # Notify customer about status change
    msg_map = {
        'Confirmed': f'✅ Order #{order.id} confirmed by restaurant!',
        'Preparing': f'👨‍🍳 Order #{order.id} is being prepared. A driver will pick it up soon!',
        'Out for Delivery': f'🛵 Order #{order.id} is on the way!',
        'Delivered': f'🎉 Order #{order.id} delivered!'
    }
    if new_status in msg_map:
        n = Notification(user_id=order.user_id, message=msg_map[new_status])
        db.session.add(n)
        db.session.commit()

    flash('Order status updated!', 'success')
    return redirect(url_for('restaurant.dashboard'))
