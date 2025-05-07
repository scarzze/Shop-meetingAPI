from flask import Blueprint, request, jsonify, current_app
from ..models import Product, Category, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_product_data
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_, func
from shared.utils.pagination import PaginationHelper
from shared.utils.cloudinary_utils import cloudinary_uploader
import logging

bp = Blueprint('product', __name__, url_prefix='/api/products')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def get_products():
    """
    Get products with pagination, filtering, and sorting
    """
    logger.info("Getting products with filters")
    
    try:
        # Get pagination parameters
        page, per_page = PaginationHelper.get_pagination_params()
        sort_by = request.args.get('sort', 'id')
        order = request.args.get('order', 'asc')
        search = request.args.get('search', '')
        category_name = request.args.get('category', '')
        min_price = request.args.get('min_price', None, type=float)
        max_price = request.args.get('max_price', None, type=float)
        
        # Build query
        query = Product.query
        
        # Apply filters
        if category_name:
            category = Category.query.filter(func.lower(Category.name) == func.lower(category_name)).first()
            if category:
                query = query.filter(Product.category_id == category.id)
                
        if search:
            search_term = f'%{search}%'
            query = query.filter(or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            ))
            
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        # Apply sorting
        if sort_by == 'price':
            query = query.order_by(Product.price.asc() if order == 'asc' else Product.price.desc())
        elif sort_by == 'name':
            query = query.order_by(Product.name.asc() if order == 'asc' else Product.name.desc())
        else:  # Default to id
            query = query.order_by(Product.id.asc() if order == 'asc' else Product.id.desc())
            
        # Use shared pagination helper
        result = PaginationHelper.paginate_query(query, Product, page, per_page)
        return jsonify(result), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_products: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    logger.info(f"Getting product with ID: {product_id}")
    
    try:
        product = Product.query.get(product_id)
        
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify(product.to_dict()), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_product: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('', methods=['POST'])
@auth_required
def create_product():
    """Create a new product"""
    logger.info("Creating new product")
    
    try:
        # Handle form data and file
        data = request.form.to_dict()
        image_file = request.files.get('image')
        
        validation_error = validate_product_data(data)
        if validation_error:
            logger.warning(f"Validation error in create_product: {validation_error}")
            return jsonify({"error": validation_error}), 400
            
        # Upload image if provided
        image_url = None
        if image_file:
            try:
                upload_result = cloudinary_uploader.upload_file(
                    image_file,
                    folder='products'
                )
                image_url = upload_result['url']
            except Exception as e:
                logger.error(f"Image upload error: {str(e)}")
                return jsonify({"error": "Failed to upload image"}), 500

        # Verify category exists
        category = Category.query.get(data['category_id'])
        if not category:
            logger.warning(f"Category not found with ID: {data['category_id']}")
            return jsonify({"error": "Category not found"}), 404

        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            category_id=data['category_id'],
            stock_quantity=data.get('stock_quantity', 0),
            sku=data.get('sku'),
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Product created successfully with ID: {product.id}")
        return jsonify(product.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in create_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
@auth_required
def update_product(product_id):
    """Update a product"""
    logger.info(f"Updating product with ID: {product_id}")
    
    try:
        data = request.form.to_dict()
        image_file = request.files.get('image')
        
        validation_error = validate_product_data(data)
        if validation_error:
            logger.warning(f"Validation error in update_product: {validation_error}")
            return jsonify({"error": validation_error}), 400
            
        product = Product.query.get(product_id)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404

        # Handle image update if provided
        if image_file:
            try:
                # Delete old image if exists
                if product.image_url and 'cloudinary' in product.image_url:
                    old_public_id = product.image_url.split('/')[-1].split('.')[0]
                    cloudinary_uploader.delete_file(old_public_id)

                # Upload new image
                upload_result = cloudinary_uploader.upload_file(
                    image_file,
                    folder='products'
                )
                data['image_url'] = upload_result['url']
            except Exception as e:
                logger.error(f"Image upload error: {str(e)}")
                return jsonify({"error": "Failed to upload image"}), 500

        # Update product fields
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        db.session.commit()
        logger.info(f"Product updated successfully with ID: {product.id}")
        return jsonify(product.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in update_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:product_id>', methods=['PATCH'])
@auth_required
def partial_update_product(product_id):
    """Partially update a product"""
    logger.info(f"Partially updating product with ID: {product_id}")
    
    data = request.get_json()
    
    if not data:
        logger.warning("No data provided for partial update")
        return jsonify({"error": "No data provided"}), 400
        
    try:
        product = Product.query.get(product_id)
        
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
            
        # Validate category_id if provided
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                logger.warning(f"Category not found with ID: {data['category_id']}")
                return jsonify({"error": "Category not found"}), 404
                
        # Check if SKU exists if being changed
        if 'sku' in data and data['sku'] != product.sku:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
                logger.warning(f"Product with SKU '{data['sku']}' already exists")
                return jsonify({"error": "Product with this SKU already exists"}), 409
                
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({"error": "Price must be a positive number"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Price must be a valid number"}), 400
                
        # Validate stock_quantity if provided
        if 'stock_quantity' in data:
            try:
                stock = int(data['stock_quantity'])
                if stock < 0:
                    return jsonify({"error": "Stock quantity cannot be negative"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Stock quantity must be a valid integer"}), 400
                
        # Update product fields
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
                
        db.session.commit()
        
        logger.info(f"Product partially updated successfully with ID: {product.id}")
        return jsonify(product.to_dict()), 200
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error in partial_update_product: {str(e)}")
        return jsonify({"error": "Product update failed due to data integrity error"}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in partial_update_product: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
@auth_required
def delete_product(product_id):
    """Delete a product"""
    logger.info(f"Deleting product with ID: {product_id}")
    
    try:
        product = Product.query.get(product_id)
        
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
            
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Product deleted successfully with ID: {product_id}")
        return jsonify({"message": "Product deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in delete_product: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
