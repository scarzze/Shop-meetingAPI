from flask import Blueprint, request, jsonify
from ..models import Review, Product, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_review_data
from sqlalchemy.exc import SQLAlchemyError
import logging

bp = Blueprint('review', __name__, url_prefix='/api/reviews')
logger = logging.getLogger(__name__)

@bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get all reviews for a product"""
    logger.info(f"Getting reviews for product ID: {product_id}")
    
    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
            
        # Get reviews
        reviews = Review.query.filter_by(product_id=product_id).all()
        
        return jsonify([review.to_dict() for review in reviews]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_product_reviews: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get review by ID"""
    logger.info(f"Getting review with ID: {review_id}")
    
    try:
        review = Review.query.get(review_id)
        
        if not review:
            logger.warning(f"Review not found with ID: {review_id}")
            return jsonify({"error": "Review not found"}), 404
            
        return jsonify(review.to_dict()), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_review: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('', methods=['POST'])
@auth_required
def create_review():
    """Create a new review"""
    logger.info("Creating new review")
    
    data = request.get_json()
    validation_error = validate_review_data(data)
    
    if validation_error:
        logger.warning(f"Validation error in create_review: {validation_error}")
        return jsonify({"error": validation_error}), 400
        
    try:
        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            logger.warning(f"Product not found with ID: {data['product_id']}")
            return jsonify({"error": "Product not found"}), 404
            
        # Get user information from auth middleware
        user_id = request.user['id']
        
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            product_id=data['product_id'],
            user_id=user_id
        ).first()
        
        if existing_review:
            logger.warning(f"User {user_id} already reviewed product {data['product_id']}")
            return jsonify({
                "error": "You have already reviewed this product",
                "review_id": existing_review.id
            }), 409
            
        review = Review(
            product_id=data['product_id'],
            user_id=user_id,
            user_name=data['user_name'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(review)
        db.session.commit()
        
        logger.info(f"Review created successfully with ID: {review.id}")
        return jsonify(review.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in create_review: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:review_id>', methods=['PUT'])
@auth_required
def update_review(review_id):
    """Update a review"""
    logger.info(f"Updating review with ID: {review_id}")
    
    data = request.get_json()
    validation_error = validate_review_data(data)
    
    if validation_error:
        logger.warning(f"Validation error in update_review: {validation_error}")
        return jsonify({"error": validation_error}), 400
        
    try:
        review = Review.query.get(review_id)
        
        if not review:
            logger.warning(f"Review not found with ID: {review_id}")
            return jsonify({"error": "Review not found"}), 404
            
        # Verify ownership or admin rights
        user_id = request.user['id']
        if review.user_id != user_id:
            logger.warning(f"User {user_id} attempted to update review {review_id} owned by {review.user_id}")
            return jsonify({"error": "You can only update your own reviews"}), 403
            
        # Verify product exists and matches
        if data['product_id'] != review.product_id:
            product = Product.query.get(data['product_id'])
            if not product:
                logger.warning(f"Product not found with ID: {data['product_id']}")
                return jsonify({"error": "Product not found"}), 404
                
        # Update review fields
        review.product_id = data['product_id']
        review.user_name = data['user_name']
        review.rating = data['rating']
        review.comment = data.get('comment', review.comment)
        
        db.session.commit()
        
        logger.info(f"Review updated successfully with ID: {review.id}")
        return jsonify(review.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in update_review: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:review_id>', methods=['DELETE'])
@auth_required
def delete_review(review_id):
    """Delete a review"""
    logger.info(f"Deleting review with ID: {review_id}")
    
    try:
        review = Review.query.get(review_id)
        
        if not review:
            logger.warning(f"Review not found with ID: {review_id}")
            return jsonify({"error": "Review not found"}), 404
            
        # Verify ownership or admin rights
        user_id = request.user['id']
        if review.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete review {review_id} owned by {review.user_id}")
            return jsonify({"error": "You can only delete your own reviews"}), 403
            
        db.session.delete(review)
        db.session.commit()
        
        logger.info(f"Review deleted successfully with ID: {review_id}")
        return jsonify({"message": "Review deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in delete_review: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
