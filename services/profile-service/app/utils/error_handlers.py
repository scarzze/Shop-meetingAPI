from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error.description)
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': str(error.description)
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': str(error.description)
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

def handle_service_error(error):
    """Handle common service communication errors"""
    if hasattr(error, 'response'):
        status_code = error.response.status_code
        try:
            error_data = error.response.json()
            message = error_data.get('message', str(error))
        except:
            message = str(error)
    else:
        status_code = 500
        message = str(error)
    
    return jsonify({
        'error': 'Service Error',
        'message': message
    }), status_code