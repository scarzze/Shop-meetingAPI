from flask import Blueprint, jsonify
import logging

bp = Blueprint('home', __name__)
logger = logging.getLogger(__name__)

@bp.route('/')
def home():
    """Home route for the Product Management service"""
    logger.info("Home endpoint accessed")
    return jsonify({
        'service': 'Product Management Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'categories': '/api/categories',
            'products': '/api/products',
            'reviews': '/api/reviews'
        }
    })

@bp.route('/health')
def health_check():
    """Health check endpoint for service monitoring"""
    logger.debug("Health check endpoint accessed")
    return jsonify({
        'status': 'healthy',
        'service': 'product'
    })
