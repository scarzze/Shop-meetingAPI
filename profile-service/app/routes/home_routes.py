from flask import Blueprint, jsonify, current_app
from app.models import db

bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET'])
def welcome():
    return jsonify({
        'message': 'Welcome to the Shop Meeting Profile Service API',
        'version': '1.0',
        'endpoints': {
            'profile': {
                'get_profile': '/profile/<user_id>',
                'update_profile': '/profile [PATCH]'
            },
            'addresses': '/addresses',
            'wishlist': '/wishlist'
        },
        'status': 'healthy'
    })

@bp.route('/health', methods=['GET'])
def health_check():
    debug_mode = current_app.config.get('DEBUG_MODE', False)
    if debug_mode:
        return jsonify({
            'status': 'healthy', 
            'mode': 'debug',
            'message': 'Running in DEBUG_MODE with mock data'
        }), 200
    else:
        try:
            # Try a simple database query to validate connection
            db.session.execute('SELECT 1').fetchall()
            return jsonify({'status': 'healthy'}), 200
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500