"""
Module for the Profile Service health check endpoint.
This is defined separately to avoid conflicts with other route definitions.
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint that always returns 200 OK.
    This is used by monitoring systems to verify that the service is running.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'profile',
        'version': '1.0.0'
    }), 200
