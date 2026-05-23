from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Restaurant, MenuItem, Order, OrderItem, Review, SavedAddress, Notification, User

customer = Blueprint('customer', __name__, url_prefix='/customer')

@customer.route('/')
@customer.route('/home')
def home():
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return render_template('customer/home.html', restaurants=restaurants)

@customer.route('/restaurant/<int:restaurant_id>')
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    items = MenuItem.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()
    categories = list(dict.fromkeys([item.category for item in items]))
    recommended = [i for i in items if i.is_recommended]
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).limit(5).all()
    cart = session.get('cart', {})
    return render_template('customer/menu.html', restaurant=restaurant, items=items,
                           categories=categories, recommended=recommended, reviews=reviews, cart=cart)

@customer.route('/cart/add', methods=['POST'])
def add_to_cart():
    item_id = str(request.form.get('item_id'))
    restaurant_id = str(request.form.get('restaurant_id'))
    cart = session.get('cart', {})
    if cart and cart.get('restaurant_id') != restaurant_id:
        cart = {}
        flash('Cart cleared — you can only order from one restaurant at a time.', 'warning')
    cart['restaurant_id'] = restaurant_id
    items = cart.get('items', {})
    items[item_id] = items.get(item_id, 0) + 1
    cart['items'] = items
    session['cart'] = cart
    flash('Item added to cart! 🛒', 'success')
    return redirect(url_for('customer.restaurant_menu', restaurant_id=restaurant_id))

@customer.route('/cart/remove/<item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    items = cart.get('items', {})
    if item_id in items:
        del items[item_id]
    cart['items'] = items
    session['cart'] = cart
    return redirect(url_for('customer.view_cart'))

@customer.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items, total, restaurant = [], 0, None
    if cart.get('items'):
        restaurant = Restaurant.query.get(cart['restaurant_id'])
        for item_id, qty in cart['items'].items():
            item = MenuItem.query.get(int(item_id))
            if item:
                subtotal = item.price * qty
                total += subtotal
                cart_items.append({'item': item, 'qty': qty, 'subtotal': subtotal})
    return render_template('customer/cart.html', cart_items=cart_items, total=total, restaurant=restaurant)

@customer.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart.get('items'):
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('customer.home'))
    cart_items, total = [], 0
    for item_id, qty in cart['items'].items():
        item = MenuItem.query.get(int(item_id))
        if item:
            subtotal = item.price * qty
            total += subtotal
            cart_items.append({'item': item, 'qty': qty, 'subtotal': subtotal})
    saved_addresses = SavedAddress.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        address = request.form.get('address')
        payment = request.form.get('payment')
        instructions = request.form.get('instructions', '')

        if address and not SavedAddress.query.filter_by(user_id=current_user.id, address=address).first():
            sa = SavedAddress(user_id=current_user.id, label='Recent', address=address)
            db.session.add(sa)

        # Order starts as "Waiting for Driver"
        order = Order(
            user_id=current_user.id,
            restaurant_id=int(cart['restaurant_id']),
            total_amount=total,
            delivery_address=address,
            payment_method=payment,
            special_instructions=instructions,
            status='Waiting for Driver',
            driver_id=None,
            eta_minutes=0
        )
        db.session.add(order)
        db.session.flush()

        for item_id, qty in cart['items'].items():
            item = MenuItem.query.get(int(item_id))
            oi = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=qty, price=item.price)
            db.session.add(oi)

        # Notify ALL available drivers
        free_drivers = User.query.filter_by(role='driver', is_available=True).all()
        for drv in free_drivers:
            n = Notification(user_id=drv.id,
                message=f'🛵 New order #{order.id} from {order.restaurant.name}! Deliver to: {address[:50]}. Accept now!')
            db.session.add(n)

        # Notify customer
        n = Notification(user_id=current_user.id,
            message=f'✅ Order #{order.id} placed! Waiting for a driver to accept your order...')
        db.session.add(n)

        db.session.commit()
        session.pop('cart', None)
        flash('Order placed! Waiting for a driver to accept. 🎉', 'success')
        return redirect(url_for('customer.order_tracking', order_id=order.id))

    return render_template('customer/checkout.html', cart_items=cart_items, total=total, saved_addresses=saved_addresses)

@customer.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=orders)

@customer.route('/order/<int:order_id>')
@login_required
def order_tracking(order_id):
    order = Order.query.get_or_404(order_id)
    statuses = ['Waiting for Driver', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered']
    current_step = statuses.index(order.status) if order.status in statuses else 0
    return render_template('customer/tracking.html', order=order, statuses=statuses, current_step=current_step)

@customer.route('/order/<int:order_id>/review', methods=['POST'])
@login_required
def submit_review(order_id):
    order = Order.query.get_or_404(order_id)
    if order.review:
        flash('You already reviewed this order!', 'warning')
        return redirect(url_for('customer.order_tracking', order_id=order_id))
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', '')
    review = Review(user_id=current_user.id, restaurant_id=order.restaurant_id,
                    order_id=order_id, rating=rating, comment=comment)
    db.session.add(review)
    rest = order.restaurant
    all_count = Review.query.filter_by(restaurant_id=rest.id).count() + 1
    total_score = sum(r.rating for r in Review.query.filter_by(restaurant_id=rest.id).all()) + rating
    rest.rating = round(total_score / all_count, 1)
    rest.total_ratings = all_count
    db.session.commit()
    flash('Thank you for your review! ⭐', 'success')
    return redirect(url_for('customer.order_tracking', order_id=order_id))

@customer.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('customer/notifications.html', notifications=notifs)

@customer.route('/api/order/<int:order_id>/status')
def order_status_api(order_id):
    order = Order.query.get_or_404(order_id)
    driver_data = None
    if order.driver:
        driver_data = {'name': order.driver.name, 'lat': order.driver.driver_lat, 'lng': order.driver.driver_lng}
    return jsonify({'status': order.status, 'eta': order.eta_minutes, 'driver': driver_data})
