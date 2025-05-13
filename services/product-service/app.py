from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
import requests
import os

from models import db, Product, Review, Favorite

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///product.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

db.init_app(app)
Migrate(app, db)

# Configure CORS
allowed_origins = ["http://127.0.0.1:5173", "http://localhost:5173", "http://localhost:3000"]
frontend_url = os.getenv('FRONTEND_URL')
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

CORS(app, 
     resources={r"/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
         "supports_credentials": True,
         "expose_headers": ["Authorization"]
     }},
     supports_credentials=True,
     allow_credentials=True
)

# Auth service URL
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')

# Helper function to validate token with auth service
def validate_token(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

@app.route('/')
def index():
    return {'message': 'Product Service API'}

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    # Optional category filter
    category = request.args.get('category')
    
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    
    return jsonify({
        'products': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'oldPrice': p.oldPrice,
            'stock': p.stock,
            'image_url': p.image_url,
            'category': p.category
        } for p in products]
    }), 200

# Get product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get reviews for this product
    reviews = [{
        'id': r.id,
        'user_id': r.user_id,
        'rating': r.rating,
        'review_text': r.review_text,
        'created_at': r.created_at.isoformat()
    } for r in product.reviews]
    
    return jsonify({
        'product': {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'oldPrice': product.oldPrice,
            'stock': product.stock,
            'image_url': product.image_url,
            'category': product.category,
            'reviews': reviews
        }
    }), 200

# Get products by category
@app.route('/categories/<category>', methods=['GET'])
def get_products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    
    return jsonify({
        'category': category,
        'products': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'oldPrice': p.oldPrice,
            'stock': p.stock,
            'image_url': p.image_url,
            'category': p.category
        } for p in products]
    }), 200

# Get all categories
@app.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({'categories': [c[0] for c in categories]}), 200

# Add review
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
def add_review(product_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.json
    rating = data.get('rating')
    review_text = data.get('review_text')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.review_text = review_text
        db.session.commit()
        return jsonify({'message': 'Review updated successfully'}), 200
    
    # Create new review
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        review_text=review_text
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review added successfully',
        'review': {
            'id': review.id,
            'user_id': review.user_id,
            'product_id': review.product_id,
            'rating': review.rating,
            'review_text': review.review_text,
            'created_at': review.created_at.isoformat()
        }
    }), 201

# Get reviews for a product
@app.route('/products/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    reviews = [{
        'id': r.id,
        'user_id': r.user_id,
        'rating': r.rating,
        'review_text': r.review_text,
        'created_at': r.created_at.isoformat()
    } for r in product.reviews]
    
    return jsonify({'reviews': reviews}), 200

# Get user's wishlist/favorites
@app.route('/favorites', methods=['GET'])
def get_wishlist():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    
    favorite_products = [{
        'id': f.product.id,
        'name': f.product.name,
        'description': f.product.description,
        'price': f.product.price,
        'oldPrice': f.product.oldPrice,
        'stock': f.product.stock,
        'image_url': f.product.image_url,
        'category': f.product.category
    } for f in favorites]
    
    return jsonify({'favorites': favorite_products}), 200

# Add to wishlist/favorites
@app.route('/favorites', methods=['POST'])
def add_to_wishlist():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if already in favorites
    existing = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return jsonify({'message': 'Product already in favorites'}), 200
    
    favorite = Favorite(user_id=user_id, product_id=product_id)
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Product added to favorites'}), 201

# Remove from wishlist/favorites
@app.route('/favorites/<int:product_id>', methods=['DELETE'])
def remove_from_wishlist(product_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    favorite = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if not favorite:
        return jsonify({'error': 'Product not in favorites'}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Product removed from favorites'}), 200

# Search products
@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Simple search implementation
    search_term = f'%{query}%'
    products = Product.query.filter(
        db.or_(
            Product.name.ilike(search_term),
            Product.description.ilike(search_term),
            Product.category.ilike(search_term)
        )
    ).all()
    
    return jsonify({
        'query': query,
        'results': [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'oldPrice': p.oldPrice,
            'stock': p.stock,
            'image_url': p.image_url,
            'category': p.category
        } for p in products]
    }), 200

# Get personalized recommendations
@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    # Get optional parameters
    limit = request.args.get('limit', 8, type=int)
    user_id = request.args.get('user_id', None)
    
    # Validate limit
    if limit < 1 or limit > 20:
        limit = 8  # Default to 8 if invalid
    
    # If user_id is provided, we could fetch user's browsing history or preferences
    # from a database to provide personalized recommendations
    # For now, we'll implement a simple recommendation algorithm
    
    # Get a mix of products from different categories
    categories = db.session.query(Product.category).distinct().limit(4).all()
    category_names = [c[0] for c in categories]
    
    recommendations = []
    
    # Get top products from each category
    for category in category_names:
        category_products = Product.query.filter_by(category=category).limit(limit // len(category_names) + 1).all()
        recommendations.extend(category_products)
    
    # Shuffle and limit to requested number
    import random
    random.shuffle(recommendations)
    recommendations = recommendations[:limit]
    
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'oldPrice': p.oldPrice,
            'stock': p.stock,
            'image_url': p.image_url,
            'category': p.category
        } for p in recommendations
    ]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
