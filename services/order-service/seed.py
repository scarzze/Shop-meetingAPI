from app import app, db
from models import Order, OrderItem, Payment
import secrets
from datetime import datetime, timedelta

with app.app_context():
    # Drop and recreate tables
    db.drop_all()
    db.create_all()

    # Create test orders
    # Order for Alice (user_id=1)
    order1 = Order(
        user_id=1,
        status="Delivered",
        shipping_address="123 Main St, Apt 4B, New York, NY 10001, USA",
        total_amount=5058,  # 2 * 1189 + 2680
        created_at=datetime.utcnow() - timedelta(days=10)
    )
    
    # Another order for Alice (user_id=1)
    order2 = Order(
        user_id=1,
        status="Processing",
        shipping_address="123 Main St, Apt 4B, New York, NY 10001, USA",
        total_amount=28999,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    
    # Order for Bob (user_id=2)
    order3 = Order(
        user_id=2,
        status="Shipped",
        shipping_address="456 Oak Ave, San Francisco, CA 94102, USA",
        total_amount=12200,  # 1 * 9600 + 2600
        created_at=datetime.utcnow() - timedelta(days=5)
    )
    
    db.session.add_all([order1, order2, order3])
    db.session.flush()  # Get order IDs without committing
    
    # Add order items
    order_items = [
        # Items for order1
        OrderItem(
            order_id=order1.id,
            product_id=1,  # HAVIT HV-G92 Gamepad
            quantity=2,
            price_at_purchase=1189,
            product_name='HAVIT HV-G92 Gamepad',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569547/HAVIT_HV-G92_Gamepad_ry0siv.jpg'
        ),
        OrderItem(
            order_id=order1.id,
            product_id=5,  # The north coat
            quantity=1,
            price_at_purchase=2680,
            product_name='The north coat',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569540/The_north_coat_jvrm3j.jpg'
        ),
        
        # Items for order2
        OrderItem(
            order_id=order2.id,
            product_id=3,  # IPS LCD Gaming Monitor
            quantity=1,
            price_at_purchase=28999,
            product_name='IPS LCD Gaming Monitor',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569546/IPS_LCD_Gaming_Monitor_ehbcvd.jpg'
        ),
        
        # Items for order3
        OrderItem(
            order_id=order3.id,
            product_id=6,  # Gucci duffle bag
            quantity=1,
            price_at_purchase=9600,
            product_name='Gucci duffle bag',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569539/Gucci_duffle_bag_mnxckr.jpg'
        ),
        OrderItem(
            order_id=order3.id,
            product_id=7,  # RGB liquid CPU Cooler
            quantity=1,
            price_at_purchase=2600,
            product_name='RGB liquid CPU Cooler',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569539/RGB_liquid_CPU_Cooler_fkvlyj.jpg'
        )
    ]
    
    db.session.add_all(order_items)
    
    # Add payments
    payments = [
        Payment(
            order_id=order1.id,
            payment_method="Credit Card",
            amount=5058,
            status="Completed",
            paid_at=datetime.utcnow() - timedelta(days=10),
            transaction_id=f"txn_{secrets.token_hex(16)}"
        ),
        Payment(
            order_id=order2.id,
            payment_method="PayPal",
            amount=28999,
            status="Completed",
            paid_at=datetime.utcnow() - timedelta(days=2),
            transaction_id=f"txn_{secrets.token_hex(16)}"
        ),
        Payment(
            order_id=order3.id,
            payment_method="Credit Card",
            amount=12200,
            status="Completed",
            paid_at=datetime.utcnow() - timedelta(days=5),
            transaction_id=f"txn_{secrets.token_hex(16)}"
        )
    ]
    
    db.session.add_all(payments)
    db.session.commit()
    
    print("Order service database seeded successfully.")
