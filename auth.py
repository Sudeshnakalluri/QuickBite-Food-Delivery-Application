from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return redirect(url_for('customer.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'restaurant':
                return redirect(url_for('restaurant.dashboard'))
            elif user.role == 'driver':
                return redirect(url_for('driver.dashboard'))
            return redirect(url_for('customer.home'))
        flash('Invalid email or password!', 'danger')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    session.pop('cart', None)
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))
