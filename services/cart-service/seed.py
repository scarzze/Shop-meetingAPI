from app import app, db
from model import Cart, CartItem

with app.app_context():
    # Drop and recreate tables
    db.drop_all()
    db.create_all()

    # Create test carts for users
    cart1 = Cart(user_id=1)  # Corresponds to 'alice' in auth service
    cart2 = Cart(user_id=2)  # Corresponds to 'bob' in auth service
    
    db.session.add_all([cart1, cart2])
    db.session.commit()
    
    # Add items to Alice's cart
    cart_items = [
        CartItem(
            cart_id=cart1.id,
            product_id=1,  # HAVIT HV-G92 Gamepad
            quantity=2,
            price=1189,
            product_name='HAVIT HV-G92 Gamepad',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569547/HAVIT_HV-G92_Gamepad_ry0siv.jpg'
        ),
        CartItem(
            cart_id=cart1.id,
            product_id=5,  # The north coat
            quantity=1,
            price=2680,
            product_name='The north coat',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569540/The_north_coat_jvrm3j.jpg'
        )
    ]
    
    # Add items to Bob's cart
    cart_items.append(
        CartItem(
            cart_id=cart2.id,
            product_id=3,  # IPS LCD Gaming Monitor
            quantity=1,
            price=28999,
            product_name='IPS LCD Gaming Monitor',
            product_image='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569546/IPS_LCD_Gaming_Monitor_ehbcvd.jpg'
        )
    )
    
    db.session.add_all(cart_items)
    db.session.commit()
    
    print("Cart service database seeded successfully.")
