from flask import Blueprint, request, jsonify, current_app
from ..models import Category, Product, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_category_data
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.shared.utils.pagination import PaginationHelper
import logging

bp = Blueprint('category', __name__, url_prefix='/api/categories')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def get_all_categories():
    """Get all categories with pagination"""
    logger.info("Getting all categories")
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock category data with pagination
        logger.info("DEBUG_MODE: Returning mock category data")
        
        # Create mock categories list
        mock_categories = [
            {
                "id": 1,
                "name": "Electronics",
                "description": "Electronic devices and gadgets",
                "created_at": "2025-01-10T09:00:00",
                "updated_at": "2025-01-10T09:00:00"
            },
            {
                "id": 2,
                "name": "Furniture",
                "description": "Home and office furniture",
                "created_at": "2025-01-10T09:15:00",
                "updated_at": "2025-01-10T09:15:00"
            },
            {
                "id": 3,
                "name": "Kitchen",
                "description": "Kitchen appliances and accessories",
                "created_at": "2025-01-10T09:30:00",
                "updated_at": "2025-01-10T09:30:00"
            },
            {
                "id": 4,
                "name": "Fitness",
                "description": "Fitness and sports equipment",
                "created_at": "2025-01-10T09:45:00",
                "updated_at": "2025-01-10T09:45:00"
            },
            {
                "id": 5,
                "name": "Clothing",
                "description": "Clothing and apparel for all ages",
                "created_at": "2025-01-10T10:00:00",
                "updated_at": "2025-01-10T10:00:00"
            }
        ]
        
        # Get pagination parameters
        page, per_page = PaginationHelper.get_pagination_params()
        
        # Apply simple pagination to mock data
        total_items = len(mock_categories)
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        paginated_categories = mock_categories[start_idx:end_idx] if start_idx < total_items else []
        
        # Format the response similar to the standard pagination format
        result = {
            "items": paginated_categories,
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
        # Get pagination parameters
        page, per_page = PaginationHelper.get_pagination_params()
        
        # Use shared pagination helper
        query = Category.query.order_by(Category.name.asc())
        result = PaginationHelper.paginate_query(query, Category, page, per_page)
        return jsonify(result), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_all_categories: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    logger.info(f"Getting category with ID: {category_id}")
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock category data based on category_id
        logger.info(f"DEBUG_MODE: Returning mock data for category ID: {category_id}")
        
        # Create a dictionary of mock categories to simulate a database
        mock_categories = {
            1: {
                "id": 1,
                "name": "Electronics",
                "description": "Electronic devices and gadgets",
                "created_at": "2025-01-10T09:00:00",
                "updated_at": "2025-01-10T09:00:00"
            },
            2: {
                "id": 2,
                "name": "Furniture",
                "description": "Home and office furniture",
                "created_at": "2025-01-10T09:15:00",
                "updated_at": "2025-01-10T09:15:00"
            },
            3: {
                "id": 3,
                "name": "Kitchen",
                "description": "Kitchen appliances and accessories",
                "created_at": "2025-01-10T09:30:00",
                "updated_at": "2025-01-10T09:30:00"
            },
            4: {
                "id": 4,
                "name": "Fitness",
                "description": "Fitness and sports equipment",
                "created_at": "2025-01-10T09:45:00",
                "updated_at": "2025-01-10T09:45:00"
            },
            5: {
                "id": 5,
                "name": "Clothing",
                "description": "Clothing and apparel for all ages",
                "created_at": "2025-01-10T10:00:00",
                "updated_at": "2025-01-10T10:00:00"
            }
        }
        
        # Return the requested category or a 404 if not found
        if category_id in mock_categories:
            return jsonify(mock_categories[category_id]), 200
        else:
            logger.warning(f"DEBUG_MODE: Mock category not found with ID: {category_id}")
            return jsonify({"error": "Category not found"}), 404
    
    # Normal database operation if not in DEBUG_MODE
    try:
        category = Category.query.get(category_id)
        
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            return jsonify({"error": "Category not found"}), 404
            
        return jsonify(category.to_dict()), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_category: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('', methods=['POST'])
@auth_required
def create_category():
    """Create a new category"""
    logger.info("Creating new category")
    
    data = request.get_json()
    validation_error = validate_category_data(data)
    
    if validation_error:
        logger.warning(f"Validation error in create_category: {validation_error}")
        return jsonify({"error": validation_error}), 400
        
    try:
        # Check for duplicate category name
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            logger.warning(f"Category with name '{data['name']}' already exists")
            return jsonify({"error": "Category with this name already exists"}), 409
            
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        logger.info(f"Category created successfully with ID: {category.id}")
        return jsonify(category.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error in create_category: {str(e)}")
        return jsonify({"error": "Category with this name already exists"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in create_category: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:category_id>', methods=['PUT'])
@auth_required
def update_category(category_id):
    """Update a category"""
    logger.info(f"Updating category with ID: {category_id}")
    
    data = request.get_json()
    validation_error = validate_category_data(data)
    
    if validation_error:
        logger.warning(f"Validation error in update_category: {validation_error}")
        return jsonify({"error": validation_error}), 400
        
    try:
        category = Category.query.get(category_id)
        
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            return jsonify({"error": "Category not found"}), 404
            
        # Check for duplicate category name if name is being changed
        if data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                logger.warning(f"Category with name '{data['name']}' already exists")
                return jsonify({"error": "Category with this name already exists"}), 409
                
        category.name = data['name']
        category.description = data.get('description', category.description)
        
        db.session.commit()
        
        logger.info(f"Category updated successfully with ID: {category.id}")
        return jsonify(category.to_dict()), 200
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error in update_category: {str(e)}")
        return jsonify({"error": "Category with this name already exists"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in update_category: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:category_id>', methods=['DELETE'])
@auth_required
def delete_category(category_id):
    """Delete a category"""
    logger.info(f"Deleting category with ID: {category_id}")
    
    try:
        category = Category.query.get(category_id)
        
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            return jsonify({"error": "Category not found"}), 404
            
        # Check if category has associated products
        products_count = Product.query.filter_by(category_id=category_id).count()
        
        if products_count > 0:
            logger.warning(f"Cannot delete category with ID {category_id}: has {products_count} associated products")
            return jsonify({
                "error": "Cannot delete category with associated products",
                "count": products_count
            }), 409
            
        db.session.delete(category)
        db.session.commit()
        
        logger.info(f"Category deleted successfully with ID: {category_id}")
        return jsonify({"message": "Category deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in delete_category: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
