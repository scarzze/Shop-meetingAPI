from flask import Blueprint, request, jsonify
from app import db
from models import Product, Category, Review
from sqlalchemy import func

bp = Blueprint('api', __name__)

# Helper function for pagination
def paginate(query, page, per_page):
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in items.items],
        'total': items.total,
        'page': items.page,
        'pages': items.pages,
        'per_page': items.per_page
    }

# CRUD for Categories
@bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 400
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.id), 201

@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

@bp.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify(category.to_dict())

@bp.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    category.name = name
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name})

@bp.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'})

# CRUD for Products
@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category_id = data.get('category_id')

    if not all([name, price, category_id]):
        return jsonify({'error': 'Name, price, and category_id are required'}), 400

    if not Category.query.get(category_id):
        return jsonify({'error': 'Category does not exist'}), 400

    product = Product(name=name, description=description, price=price, category_id=category_id)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_name = request.args.get('category')
    sort = request.args.get('sort')

    query = Product.query

    if category_name:
        query = query.join(Category).filter(Category.name.ilike(f'%{category_name}%'))

    if sort == 'price':
        query = query.order_by(Product.price)
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    products = paginated.items

    result = []
    for product in products:
        prod_dict = product.to_dict()
        result.append(prod_dict)

    return jsonify({
        'items': result,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    product_dict = product.to_dict()
    product_dict['reviews'] = [review.to_dict() for review in product.reviews]
    return jsonify(product_dict)

@bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category_id = data.get('category_id')

    if category_id and not Category.query.get(category_id):
        return jsonify({'error': 'Category does not exist'}), 400

    if name:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if category_id is not None:
        product.category_id = category_id

    db.session.commit()
    return jsonify(product.to_dict())

@bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

# CRUD for Reviews
@bp.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    product_id = data.get('product_id')
    user_name = data.get('user_name')
    rating = data.get('rating')
    comment = data.get('comment')

    if not all([product_id, user_name, rating]):
        return jsonify({'error': 'product_id, user_name, and rating are required'}), 400

    if not Product.query.get(product_id):
        return jsonify({'error': 'Product does not exist'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    review = Review(product_id=product_id, user_name=user_name, rating=int(rating), comment=comment)
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201

@bp.route('/reviews/<int:id>', methods=['GET'])
def get_review(id):
    review = Review.query.get_or_404(id)
    return jsonify(review.to_dict())

@bp.route('/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    review = Review.query.get_or_404(id)
    data = request.get_json()
    user_name = data.get('user_name')
    rating = data.get('rating')
    comment = data.get('comment')

    if rating is not None and not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    if user_name:
        review.user_name = user_name
    if rating is not None:
        review.rating = rating
    if comment is not None:
        review.comment = comment

    db.session.commit()
    return jsonify(review.to_dict())

@bp.route('/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'})
