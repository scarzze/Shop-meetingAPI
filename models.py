from app import db
from sqlalchemy.sql import func

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def average_rating(self):
        if not self.reviews:
            return None
        return sum([r.rating for r in self.reviews]) / len(self.reviews)

    def review_count(self):
        return len(self.reviews)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'average_rating': self.average_rating() or 0,
            'review_count': self.review_count()
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'comment': self.comment
        }
