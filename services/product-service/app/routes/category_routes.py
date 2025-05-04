from flask import Blueprint, request, jsonify, current_app
from ..models import Category, Product, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_category_data
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

bp = Blueprint('category', __name__, url_prefix='/api/categories')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def get_all_categories():
    """Get all categories"""
    logger.info("Getting all categories")
    
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories]), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in get_all_categories: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    logger.info(f"Getting category with ID: {category_id}")
    
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
