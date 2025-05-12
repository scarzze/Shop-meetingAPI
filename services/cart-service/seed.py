import os
from dotenv import load_dotenv
from app import app
from models import db, User, Product, CartItem, Order, OrderItem
from datetime import datetime

load_dotenv()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Users
    user1 = User(username='john_doe')
    user2 = User(username='jane_smith')
    user3 = User(username='mike_brown')

    # Products
    product1 = Product(name='Laptop', price=26000, stock=50)
    product2 = Product(name='Headphones', price=1200, stock=25)
    product3 = Product(name='Smartphone', price=18000, stock=10)

    db.session.add_all([user1, user2, user3, product1, product2, product3])
    db.session.commit()

    # CartItems
    cart_item1 = CartItem(user_id=user1.id, product_id=product1.id, quantity=1)
    cart_item2 = CartItem(user_id=user2.id, product_id=product2.id, quantity=2)
    cart_item3 = CartItem(user_id=user3.id, product_id=product3.id, quantity=1)

    db.session.add_all([cart_item1, cart_item2, cart_item3])
    db.session.commit()

    # Orders (placed orders, separate from cart)
    order1 = Order(user_id=user1.id, total=26000, created_at=datetime.utcnow())
    order2 = Order(user_id=user2.id, total=2400, created_at=datetime.utcnow())
    order3 = Order(user_id=user3.id, total=18000, created_at=datetime.utcnow())

    db.session.add_all([order1, order2, order3])
    db.session.flush()  # ensures we get the IDs before committing

    # OrderItems (linked to orders above)
    order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=1, price=26000)
    order_item2 = OrderItem(order_id=order2.id, product_id=product2.id, quantity=2, price=2400)
    order_item3 = OrderItem(order_id=order3.id, product_id=product3.id, quantity=1, price=18000)

    db.session.add_all([order_item1, order_item2, order_item3])
    db.session.commit()

    print("Database seeded with users, products, cart items, orders, and order items!")