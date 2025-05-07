from flask import Blueprint, request, jsonify
from ..models import Review, Product, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_review_data
from sqlalchemy.exc import SQLAlchemyError
from app.shared.utils.pagination import PaginationHelper
import logging

bp = Blueprint('review', __name__, url_prefix='/api/reviews')
logger = logging.getLogger(__name__)

@bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get all reviews for a product with pagination"""
    logger.info(f"Getting reviews for product ID: {product_id}")
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock review data with pagination
        logger.info(f"DEBUG_MODE: Returning mock review data for product ID: {product_id}")
        
        # Create mock reviews for various products
        mock_reviews = {
            1: [  # Reviews for product ID 1 (Premium Headphones)
                {
                    "id": 101,
                    "product_id": 1,
                    "user_id": 201,
                    "username": "audiophile89",
                    "rating": 5,
                    "comment": "Best headphones I've ever owned! The sound quality is exceptional and the noise cancellation works perfectly.",
                    "created_at": "2025-04-20T14:30:00",
                    "updated_at": "2025-04-20T14:30:00"
                },
                {
                    "id": 102,
                    "product_id": 1,
                    "user_id": 202,
                    "username": "musiclover42",
                    "rating": 4,
                    "comment": "Great headphones, very comfortable to wear for hours. Battery life could be better though.",
                    "created_at": "2025-04-15T09:45:00",
                    "updated_at": "2025-04-15T09:45:00"
                },
                {
                    "id": 103,
                    "product_id": 1,
                    "user_id": 203,
                    "username": "basshead77",
                    "rating": 5,
                    "comment": "The bass response is incredible! These headphones handle every genre of music beautifully.",
                    "created_at": "2025-04-10T16:20:00",
                    "updated_at": "2025-04-10T16:20:00"
                }
            ],
            2: [  # Reviews for product ID 2 (Ergonomic Office Chair)
                {
                    "id": 104,
                    "product_id": 2,
                    "user_id": 204,
                    "username": "remoteworker23",
                    "rating": 5,
                    "comment": "This chair saved my back! After switching to this, my back pain disappeared within a week.",
                    "created_at": "2025-04-18T11:10:00",
                    "updated_at": "2025-04-18T11:10:00"
                },
                {
                    "id": 105,
                    "product_id": 2,
                    "user_id": 205,
                    "username": "ergonomicsexpert",
                    "rating": 4,
                    "comment": "Great chair with excellent lumbar support. The armrests could use more padding though.",
                    "created_at": "2025-04-12T13:35:00",
                    "updated_at": "2025-04-12T13:35:00"
                }
            ],
            3: [  # Reviews for product ID 3 (Ultra-Slim Laptop)
                {
                    "id": 106,
                    "product_id": 3,
                    "user_id": 206,
                    "username": "techreviewerguy",
                    "rating": 5,
                    "comment": "Blazing fast performance in an incredibly slim package. The battery life exceeds expectations!",
                    "created_at": "2025-04-22T10:25:00",
                    "updated_at": "2025-04-22T10:25:00"
                },
                {
                    "id": 107,
                    "product_id": 3,
                    "user_id": 207,
                    "username": "codingprofessional",
                    "rating": 5,
                    "comment": "Perfect for development work. Handles multiple VMs and docker containers without breaking a sweat.",
                    "created_at": "2025-04-17T15:40:00",
                    "updated_at": "2025-04-17T15:40:00"
                },
                {
                    "id": 108,
                    "product_id": 3,
                    "user_id": 208,
                    "username": "designernomad",
                    "rating": 4,
                    "comment": "Great for graphic design work on the go. The display is gorgeous but it can get a bit hot under heavy loads.",
                    "created_at": "2025-04-05T09:15:00",
                    "updated_at": "2025-04-05T09:15:00"
                }
            ]
        }
        
        # Default to an empty list if product_id doesn't exist in our mock data
        reviews_for_product = mock_reviews.get(product_id, [])
        
        # Get pagination parameters
        page, per_page = PaginationHelper.get_pagination_params()
        
        # Apply pagination to mock data
        total_items = len(reviews_for_product)
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        paginated_reviews = reviews_for_product[start_idx:end_idx] if start_idx < total_items else []
        
        # Format the response similar to the standard pagination format
        result = {
            "items": paginated_reviews,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return jsonify(result), 200
    
    # Normal database operation if not in DEBUG_MODE
    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
            
        # Get pagination parameters
        page, per_page = PaginationHelper.get_pagination_params()
        
        # Build query with sorting by date
        query = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc())
        
        # Use shared pagination helper
        result = PaginationHelper.paginate_query(query, Review, page, per_page)
        return jsonify(result), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_product_reviews: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Get review by ID"""
    logger.info(f"Getting review with ID: {review_id}")
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock review data based on review_id
        logger.info(f"DEBUG_MODE: Returning mock data for review ID: {review_id}")
        
        # Create a dictionary of mock reviews to simulate a database
        mock_reviews = {
            101: {
                "id": 101,
                "product_id": 1,
                "user_id": 201,
                "username": "audiophile89",
                "rating": 5,
                "comment": "Best headphones I've ever owned! The sound quality is exceptional and the noise cancellation works perfectly.",
                "created_at": "2025-04-20T14:30:00",
                "updated_at": "2025-04-20T14:30:00"
            },
            102: {
                "id": 102,
                "product_id": 1,
                "user_id": 202,
                "username": "musiclover42",
                "rating": 4,
                "comment": "Great headphones, very comfortable to wear for hours. Battery life could be better though.",
                "created_at": "2025-04-15T09:45:00",
                "updated_at": "2025-04-15T09:45:00"
            },
            103: {
                "id": 103,
                "product_id": 1,
                "user_id": 203,
                "username": "basshead77",
                "rating": 5,
                "comment": "The bass response is incredible! These headphones handle every genre of music beautifully.",
                "created_at": "2025-04-10T16:20:00",
                "updated_at": "2025-04-10T16:20:00"
            },
            104: {
                "id": 104,
                "product_id": 2,
                "user_id": 204,
                "username": "remoteworker23",
                "rating": 5,
                "comment": "This chair saved my back! After switching to this, my back pain disappeared within a week.",
                "created_at": "2025-04-18T11:10:00",
                "updated_at": "2025-04-18T11:10:00"
            },
            105: {
                "id": 105,
                "product_id": 2,
                "user_id": 205,
                "username": "ergonomicsexpert",
                "rating": 4,
                "comment": "Great chair with excellent lumbar support. The armrests could use more padding though.",
                "created_at": "2025-04-12T13:35:00",
                "updated_at": "2025-04-12T13:35:00"
            },
            106: {
                "id": 106,
                "product_id": 3,
                "user_id": 206,
                "username": "techreviewerguy",
                "rating": 5,
                "comment": "Blazing fast performance in an incredibly slim package. The battery life exceeds expectations!",
                "created_at": "2025-04-22T10:25:00",
                "updated_at": "2025-04-22T10:25:00"
            },
            107: {
                "id": 107,
                "product_id": 3,
                "user_id": 207,
                "username": "codingprofessional",
                "rating": 5,
                "comment": "Perfect for development work. Handles multiple VMs and docker containers without breaking a sweat.",
                "created_at": "2025-04-17T15:40:00",
                "updated_at": "2025-04-17T15:40:00"
            },
            108: {
                "id": 108,
                "product_id": 3,
                "user_id": 208,
                "username": "designernomad",
                "rating": 4,
                "comment": "Great for graphic design work on the go. The display is gorgeous but it can get a bit hot under heavy loads.",
                "created_at": "2025-04-05T09:15:00",
                "updated_at": "2025-04-05T09:15:00"
            }
        }
        
        # Return the requested review or a 404 if not found
        if review_id in mock_reviews:
            return jsonify(mock_reviews[review_id]), 200
        else:
            logger.warning(f"DEBUG_MODE: Mock review not found with ID: {review_id}")
            return jsonify({"error": "Review not found"}), 404
    
    # Normal database operation if not in DEBUG_MODE
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
