from flask import Blueprint, jsonify, request
import requests
from app.models import Profile, WishlistItem, db
from app.utils.suggestions import get_product_suggestions
from config import Config
from app.auth.middleware import auth_required  # local auth package

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@bp.route('/', methods=['GET'])
@auth_required
def get_wishlist():
    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    items = WishlistItem.query.filter_by(profile_id=profile.id).all()
    product_ids = [item.product_id for item in items]

    products = []
    for pid in product_ids:
        try:
            resp = requests.get(f"{Config.PRODUCT_SERVICE_URL}/products/{pid}")
            if resp.ok:
                products.append(resp.json())
        except requests.RequestException:
            continue

    return jsonify({'wishlist': products})

@bp.route('/<string:product_id>', methods=['POST'])
@auth_required
def add_to_wishlist(product_id):
    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    if WishlistItem.query.filter_by(profile_id=profile.id, product_id=product_id).first():
        return jsonify({'message': 'Product already in wishlist'}), 400

    item = WishlistItem(profile_id=profile.id, product_id=product_id)
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Product added to wishlist'})

@bp.route('/<string:product_id>', methods=['DELETE'])
@auth_required
def remove_from_wishlist(product_id):
    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    item = WishlistItem.query.filter_by(profile_id=profile.id, product_id=product_id).first()
    if not item:
        return jsonify({'message': 'Product not found in wishlist'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Product removed from wishlist'})

@bp.route('/suggestions', methods=['GET'])
@auth_required
def get_suggestions():
    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    suggestions = get_product_suggestions(profile)
    return jsonify({'suggestions': suggestions})
