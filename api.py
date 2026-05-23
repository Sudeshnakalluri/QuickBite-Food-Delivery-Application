from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Notification, Order

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/notifications/unread')
@login_required
def unread_notifications():
    notifs = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'time': n.created_at.strftime('%H:%M')
    } for n in notifs])

@api.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    n = Notification.query.get_or_404(notif_id)
    n.is_read = True
    from extensions import db
    db.session.commit()
    return jsonify({'success': True})
