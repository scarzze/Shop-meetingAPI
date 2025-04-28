from flask import Blueprint, jsonify, request
import requests
from app.models import Profile, WishlistItem, db
from flask_jwt_extended import jwt_required, get_jwt_identity


from app.utils.suggestions import get_product_suggestions
from config import Config

bp = Blueprint('wishlist', __name__)

@bp.route('/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist(current_user_id):
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    wishlist_items = WishlistItem.query.filter_by(profile_id=profile.id).all()
    product_ids = [item.product_id for item in wishlist_items]
    
    # Fetch product details from product service
    products = []
    for product_id in product_ids:
        try:
            response = requests.get(f"{Config.PRODUCT_SERVICE_URL}/products/{product_id}")
            if response.status_code == 200:
                products.append(response.json())
        except requests.RequestException:
            continue
    
    return jsonify({
        'wishlist': products
    })

@bp.route('/wishlist/<product_id>', methods=['POST'])
@jwt_required()
def add_to_wishlist(current_user_id, product_id):
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    existing_item = WishlistItem.query.filter_by(
        profile_id=profile.id,
        product_id=product_id
    ).first()
    
    if existing_item:
        return jsonify({'message': 'Product already in wishlist'}), 400
    
    wishlist_item = WishlistItem(profile_id=profile.id, product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Product added to wishlist'})

@bp.route('/wishlist/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(current_user_id, product_id):
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    wishlist_item = WishlistItem.query.filter_by(
        profile_id=profile.id,
        product_id=product_id
    ).first()
    
    if not wishlist_item:
        return jsonify({'message': 'Product not found in wishlist'}), 404
    
    db.session.delete(wishlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Product removed from wishlist'})

@bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions(current_user_id):
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    suggestions = get_product_suggestions(profile)
    return jsonify({'suggestions': suggestions})