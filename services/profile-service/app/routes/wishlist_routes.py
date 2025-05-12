from flask import Blueprint, jsonify, request
import requests
from app.models import Profile, WishlistItem, db
from app.auth.middleware import auth_required
from config import Config
import logging
import os

bp = Blueprint('wishlist', __name__)
logger = logging.getLogger(__name__)

@bp.route('/wishlist', methods=['GET'])
@auth_required
def get_wishlist():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock wishlist data
    if debug_mode:
        mock_wishlist = [
            {
                'id': 1,
                'product_id': 1,
                'product': {
                    'id': 1,
                    'name': 'Premium Wireless Headphones',
                    'price': 199.99,
                    'description': 'High-quality wireless headphones with noise cancellation',
                    'image_url': 'https://example.com/images/headphones.jpg'
                },
                'added_at': '2025-05-01T10:30:00'
            },
            {
                'id': 2,
                'product_id': 3,
                'product': {
                    'id': 3,
                    'name': 'Smart Watch Pro',
                    'price': 299.99,
                    'description': 'Advanced smartwatch with health monitoring features',
                    'image_url': 'https://example.com/images/smartwatch.jpg'
                },
                'added_at': '2025-05-03T14:15:00'
            }
        ]
        logger.info("Returning mock wishlist data in DEBUG_MODE")
        return jsonify(mock_wishlist), 200
    
    # Not in DEBUG_MODE - use database
    current_user_id = request.user_id
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    wishlist_items = WishlistItem.query.filter_by(profile_id=profile.id).all()
    product_ids = [item.product_id for item in wishlist_items]
    
    # Fetch product details from product service
    products = []
    failed_products = []
    for product_id in product_ids:
        try:
            response = requests.get(
                f"{Config.PRODUCT_SERVICE_URL}/products/{product_id}",
                timeout=5
            )
            if response.status_code == 200:
                products.append(response.json())
            else:
                failed_products.append(product_id)
                logger.error(f"Failed to fetch product {product_id}: Status {response.status_code}")
        except requests.RequestException as e:
            failed_products.append(product_id)
            logger.error(f"Failed to fetch product {product_id}: {str(e)}")
    
    result = {
        'wishlist': products,
        'total_items': len(products)
    }
    
    if failed_products:
        result['failed_products'] = failed_products
        result['message'] = 'Some products could not be fetched'
    
    return jsonify(result)

@bp.route('/wishlist/<product_id>', methods=['POST'])
@auth_required
def add_to_wishlist(product_id):
    current_user_id = request.user_id
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    # Verify product exists
    try:
        response = requests.get(
            f"{Config.PRODUCT_SERVICE_URL}/products/{product_id}",
            timeout=5
        )
        if response.status_code == 404:
            return jsonify({'message': 'Product not found'}), 404
        elif response.status_code != 200:
            logger.error(f"Product service error: Status {response.status_code}")
            return jsonify({'message': 'Unable to verify product'}), 502
    except requests.RequestException as e:
        logger.error(f"Failed to verify product {product_id}: {str(e)}")
        return jsonify({'message': 'Product service unavailable'}), 503
    
    # Check if item already exists
    existing_item = WishlistItem.query.filter_by(
        profile_id=profile.id,
        product_id=product_id
    ).first()
    
    if existing_item:
        return jsonify({'message': 'Product already in wishlist'}), 400
    
    try:
        wishlist_item = WishlistItem(profile_id=profile.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to add product to wishlist'}), 500
    
    return jsonify({'message': 'Product added to wishlist'})

@bp.route('/wishlist/<product_id>', methods=['DELETE'])
@auth_required
def remove_from_wishlist(product_id):
    current_user_id = request.user_id
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    wishlist_item = WishlistItem.query.filter_by(
        profile_id=profile.id,
        product_id=product_id
    ).first()
    
    if not wishlist_item:
        return jsonify({'message': 'Product not found in wishlist'}), 404
    
    try:
        db.session.delete(wishlist_item)
        db.session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to remove product from wishlist'}), 500
    
    return jsonify({'message': 'Product removed from wishlist'})