from flask import Blueprint, jsonify

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