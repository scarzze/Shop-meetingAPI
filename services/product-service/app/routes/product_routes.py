from flask import Blueprint, request, jsonify, current_app
from ..models import Product, Category, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_product_data
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_, func
from app.shared.utils.pagination import PaginationHelper
# from app.shared.utils.cloudinary_utils import cloudinary_uploader  # Commented out until we implement this
import logging

bp = Blueprint('product', __name__, url_prefix='/api/v1/products')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
def get_products():
    """
    Get products with pagination, filtering, and sorting
    """
    logger.info("Getting products with filters")
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Get pagination parameters
    page, per_page = PaginationHelper.get_pagination_params()
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search', '')
    category_name = request.args.get('category', '')
    min_price = request.args.get('min_price', None, type=float)
    max_price = request.args.get('max_price', None, type=float)
    
    if debug_mode:
        # In DEBUG_MODE, return mock product data with filtering and pagination
        logger.info("DEBUG_MODE: Returning mock product data with filters")
        
        # Create mock products list
        mock_products = [
            {
                "id": 1,
                "name": "Premium Headphones",
                "description": "High-quality noise-cancelling headphones with superior sound",
                "price": 299.99,
                "stock": 50,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/headphones.jpg",
                "avg_rating": 4.7,
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-05-01T14:45:00"
            },
            {
                "id": 2,
                "name": "Ergonomic Office Chair",
                "description": "Comfortable ergonomic chair with lumbar support and adjustable height",
                "price": 249.99,
                "stock": 35,
                "category_id": 2,
                "category_name": "Furniture",
                "image_url": "https://example.com/images/chair.jpg",
                "avg_rating": 4.5,
                "created_at": "2025-02-10T09:15:00",
                "updated_at": "2025-04-20T11:30:00"
            },
            {
                "id": 3,
                "name": "Ultra-Slim Laptop",
                "description": "Powerful and lightweight laptop with 16GB RAM and 1TB SSD",
                "price": 1299.99,
                "stock": 20,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/laptop.jpg",
                "avg_rating": 4.8,
                "created_at": "2025-01-20T13:45:00",
                "updated_at": "2025-04-15T10:20:00"
            },
            {
                "id": 4,
                "name": "Wireless Charging Pad",
                "description": "Fast wireless charging pad compatible with all Qi-enabled devices",
                "price": 49.99,
                "stock": 100,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/charger.jpg",
                "avg_rating": 4.3,
                "created_at": "2025-03-05T16:20:00",
                "updated_at": "2025-05-02T09:10:00"
            },
            {
                "id": 5,
                "name": "Smart Home Hub",
                "description": "Central control for all your smart home devices with voice commands",
                "price": 129.99,
                "stock": 45,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/smarthub.jpg",
                "avg_rating": 4.6,
                "created_at": "2025-02-25T11:00:00",
                "updated_at": "2025-04-30T15:45:00"
            },
            {
                "id": 6,
                "name": "Stainless Steel Water Bottle",
                "description": "Vacuum insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours",
                "price": 34.99,
                "stock": 150,
                "category_id": 3,
                "category_name": "Kitchen",
                "image_url": "https://example.com/images/bottle.jpg",
                "avg_rating": 4.9,
                "created_at": "2025-03-10T08:20:00",
                "updated_at": "2025-05-01T12:30:00"
            },
            {
                "id": 7,
                "name": "Fitness Tracker",
                "description": "Water-resistant fitness tracker with heart rate monitoring and sleep tracking",
                "price": 89.99,
                "stock": 75,
                "category_id": 4,
                "category_name": "Fitness",
                "image_url": "https://example.com/images/tracker.jpg",
                "avg_rating": 4.4,
                "created_at": "2025-02-05T14:10:00",
                "updated_at": "2025-04-25T09:40:00"
            },
            {
                "id": 8,
                "name": "LED Desk Lamp",
                "description": "Adjustable LED desk lamp with multiple brightness levels and color temperatures",
                "price": 59.99,
                "stock": 60,
                "category_id": 2,
                "category_name": "Furniture",
                "image_url": "https://example.com/images/lamp.jpg",
                "avg_rating": 4.6,
                "created_at": "2025-01-30T11:25:00",
                "updated_at": "2025-04-10T15:50:00"
            }
        ]
        
        # Apply filters to mock data
        filtered_products = mock_products.copy()
        
        # Filter by category
        if category_name:
            filtered_products = [p for p in filtered_products if p["category_name"].lower() == category_name.lower()]
        
        # Filter by search term
        if search:
            search = search.lower()
            filtered_products = [p for p in filtered_products if 
                               search in p["name"].lower() or 
                               search in p["description"].lower()]
        
        # Filter by price range
        if min_price is not None:
            filtered_products = [p for p in filtered_products if p["price"] >= min_price]
            
        if max_price is not None:
            filtered_products = [p for p in filtered_products if p["price"] <= max_price]
        
        # Apply sorting
        reverse_order = order.lower() != 'asc'
        if sort_by == 'price':
            filtered_products.sort(key=lambda x: x["price"], reverse=reverse_order)
        elif sort_by == 'name':
            filtered_products.sort(key=lambda x: x["name"], reverse=reverse_order)
        else:  # Default to id
            filtered_products.sort(key=lambda x: x["id"], reverse=reverse_order)
        
        # Apply pagination
        total_items = len(filtered_products)
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        paginated_products = filtered_products[start_idx:end_idx] if start_idx < total_items else []
        
        # Format the response similar to the standard pagination format
        result = {
            "items": paginated_products,
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
    
    # Check if DEBUG_MODE is enabled
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock product data based on product_id
        logger.info(f"DEBUG_MODE: Returning mock data for product ID: {product_id}")
        
        # Create a dictionary of mock products to simulate a database
        mock_products = {
            1: {
                "id": 1,
                "name": "Premium Headphones",
                "description": "High-quality noise-cancelling headphones with superior sound",
                "price": 299.99,
                "stock": 50,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/headphones.jpg",
                "avg_rating": 4.7,
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-05-01T14:45:00"
            },
            2: {
                "id": 2,
                "name": "Ergonomic Office Chair",
                "description": "Comfortable ergonomic chair with lumbar support and adjustable height",
                "price": 249.99,
                "stock": 35,
                "category_id": 2,
                "category_name": "Furniture",
                "image_url": "https://example.com/images/chair.jpg",
                "avg_rating": 4.5,
                "created_at": "2025-02-10T09:15:00",
                "updated_at": "2025-04-20T11:30:00"
            },
            3: {
                "id": 3,
                "name": "Ultra-Slim Laptop",
                "description": "Powerful and lightweight laptop with 16GB RAM and 1TB SSD",
                "price": 1299.99,
                "stock": 20,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/laptop.jpg",
                "avg_rating": 4.8,
                "created_at": "2025-01-20T13:45:00",
                "updated_at": "2025-04-15T10:20:00"
            },
            4: {
                "id": 4,
                "name": "Wireless Charging Pad",
                "description": "Fast wireless charging pad compatible with all Qi-enabled devices",
                "price": 49.99,
                "stock": 100,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/charger.jpg",
                "avg_rating": 4.3,
                "created_at": "2025-03-05T16:20:00",
                "updated_at": "2025-05-02T09:10:00"
            },
            5: {
                "id": 5,
                "name": "Smart Home Hub",
                "description": "Central control for all your smart home devices with voice commands",
                "price": 129.99,
                "stock": 45,
                "category_id": 1,
                "category_name": "Electronics",
                "image_url": "https://example.com/images/smarthub.jpg",
                "avg_rating": 4.6,
                "created_at": "2025-02-25T11:00:00",
                "updated_at": "2025-04-30T15:45:00"
            }
        }
        
        # Return the requested product or a 404 if not found
        if product_id in mock_products:
            return jsonify(mock_products[product_id]), 200
        else:
            logger.warning(f"DEBUG_MODE: Mock product not found with ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
    
    # Normal database operation if not in DEBUG_MODE
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
