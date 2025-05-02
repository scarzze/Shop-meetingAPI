from functools import wraps
from flask import current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError

# Keeping basic error handling functionality if needed in the future
def handle_database_error(error):
    """Handler for database errors"""
    return jsonify({
        'status': 'error',
        'message': 'Database error occurred',
    }), 503