from app import create_app, db
from models import Category, Product, Review
from sqlalchemy import text

app = create_app()
app.app_context().push()

def seed_data():
    # Create tables if they don't exist
    db.create_all()

    # Clear existing data safely
    db.session.execute(text('TRUNCATE TABLE reviews RESTART IDENTITY CASCADE;'))
    db.session.execute(text('TRUNCATE TABLE products RESTART IDENTITY CASCADE;'))
    db.session.execute(text('TRUNCATE TABLE categories RESTART IDENTITY CASCADE;'))
    db.session.commit()

    # Create categories
    shoes = Category(name='Shoes')
    electronics = Category(name='Electronics')
    db.session.add_all([shoes, electronics])
    db.session.commit()

    # Create products
    product1 = Product(name='Running Shoes', description='Comfortable running shoes', price=99.99, category_id=shoes.id)
    product2 = Product(name='Smartphone', description='Latest model smartphone', price=699.99, category_id=electronics.id)
    db.session.add_all([product1, product2])
    db.session.commit()

    # Create reviews
    review1 = Review(product_id=product1.id, user_name='Alice', rating=5, comment='Great shoes!')
    review2 = Review(product_id=product2.id, user_name='Bob', rating=4, comment='Good phone but battery life could be better.')
    db.session.add_all([review1, review2])
    db.session.commit()

    print('Database seeded successfully.')

if __name__ == '__main__':
    seed_data()
