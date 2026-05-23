from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Restaurant, Order

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access only!', 'danger')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_restaurants = Restaurant.query.count()
    total_orders = Order.query.count()
    total_revenue = sum(o.total_amount for o in Order.query.all())
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
        total_users=total_users, total_restaurants=total_restaurants,
        total_orders=total_orders, total_revenue=total_revenue,
        recent_orders=recent_orders)

@admin.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin.route('/restaurants')
@login_required
@admin_required
def restaurants():
    all_restaurants = Restaurant.query.all()
    return render_template('admin/restaurants.html', restaurants=all_restaurants)

@admin.route('/restaurant/<int:r_id>/toggle')
@login_required
@admin_required
def toggle_restaurant(r_id):
    r = Restaurant.query.get_or_404(r_id)
    r.is_active = not r.is_active
    db.session.commit()
    flash(f'Restaurant {"activated" if r.is_active else "deactivated"}!', 'info')
    return redirect(url_for('admin.restaurants'))
