from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Order, Notification, User

driver = Blueprint('driver', __name__, url_prefix='/driver')

def driver_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'driver':
            flash('Driver access only!', 'danger')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated

@driver.route('/dashboard')
@login_required
@driver_required
def dashboard():
    # Orders waiting for any driver to accept
    available_orders = Order.query.filter_by(
        driver_id=None, status='Waiting for Driver').all()

    # Orders this driver accepted and is handling
    my_active_orders = Order.query.filter_by(
        driver_id=current_user.id).filter(
        Order.status.in_(['Confirmed', 'Preparing', 'Out for Delivery'])).all()

    # Completed by this driver
    completed_orders = Order.query.filter_by(
        driver_id=current_user.id, status='Delivered').order_by(
        Order.created_at.desc()).limit(10).all()

    return render_template('driver/dashboard.html',
                           available_orders=available_orders,
                           my_active_orders=my_active_orders,
                           completed=completed_orders)

@driver.route('/order/<int:order_id>/accept', methods=['POST'])
@login_required
@driver_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Check if another driver already accepted it
    if order.driver_id is not None:
        flash('Sorry! Another driver already accepted this order. 😔', 'warning')
        return redirect(url_for('driver.dashboard'))

    # Check it's still waiting
    if order.status != 'Waiting for Driver':
        flash('This order is no longer available.', 'warning')
        return redirect(url_for('driver.dashboard'))

    # Assign this driver
    order.driver_id = current_user.id
    order.status = 'Confirmed'
    order.eta_minutes = 30
    current_user.is_available = False

    # Notify customer — driver accepted!
    n = Notification(user_id=order.user_id,
        message=f'🎉 Driver {current_user.name} accepted your order #{order.id}! Your food will be delivered soon.')
    db.session.add(n)
    db.session.commit()

    flash(f'✅ You accepted Order #{order.id}! Go pick it up.', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/order/<int:order_id>/pickup', methods=['POST'])
@login_required
@driver_required
def mark_picked_up(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Out for Delivery'
    order.eta_minutes = 15
    n = Notification(user_id=order.user_id,
        message=f'🛵 Your order #{order.id} has been picked up! On the way to you.')
    db.session.add(n)
    db.session.commit()
    flash('Marked as picked up! 📦', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/order/<int:order_id>/delivered', methods=['POST'])
@login_required
@driver_required
def mark_delivered(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Delivered'
    order.eta_minutes = 0
    current_user.is_available = True
    n = Notification(user_id=order.user_id,
        message=f'✅ Order #{order.id} delivered! Enjoy your meal 🍕 Please rate your experience.')
    db.session.add(n)
    db.session.commit()
    flash('Order delivered! Great job! 🎉', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/api/location', methods=['POST'])
@login_required
@driver_required
def update_location():
    data = request.get_json()
    current_user.driver_lat = data.get('lat', current_user.driver_lat)
    current_user.driver_lng = data.get('lng', current_user.driver_lng)
    db.session.commit()
    return jsonify({'success': True})
