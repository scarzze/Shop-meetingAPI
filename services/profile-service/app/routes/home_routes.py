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

# Health check moved to main app in __init__.py to avoid routing conflicts
# @bp.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         'status': 'healthy',
#         'service': 'profile',
#         'version': '1.0.0'
#     }), 200