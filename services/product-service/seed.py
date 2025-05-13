from app import app, db
from models import Product, Review, Favorite
from dotenv import load_dotenv
import random
import cloudinary
import cloudinary.uploader
import os

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

with app.app_context():
    # Drop and recreate tables
    db.drop_all()
    db.create_all()

    # Create products from original categories
    original_products = [
        Product(name='HAVIT HV-G92 Gamepad', description='High-quality gamepad for gaming enthusiasts.', price=1189, oldPrice=1500, stock=50, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569547/HAVIT_HV-G92_Gamepad_ry0siv.jpg', category='Flash Sales'),
        Product(name='AK-900 Wired Keyboard', description='Durable wired keyboard for everyday use.', price=962, oldPrice=1200, stock=75, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569547/AK-900_Wired_Keyboard_wyzsqw.jpg', category='Flash Sales'),
        Product(name='IPS LCD Gaming Monitor', description='High-resolution gaming monitor.', price=28999, oldPrice=32999, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569546/IPS_LCD_Gaming_Monitor_ehbcvd.jpg', category='Flash Sales'),
        Product(name='S-Series Comfort Chair', description='Ergonomic chair for comfort.', price=3750, oldPrice=4500, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569546/S-Series_Comfort_Chair_vxy9fm.jpg', category='Flash Sales'),
        Product(name='The north coat', description='Stylish and warm coat.', price=2680, oldPrice=3256, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569540/The_north_coat_jvrm3j.jpg', category='Best Selling'),
        Product(name='Gucci duffle bag', description='Luxury duffle bag.', price=9600, oldPrice=12000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569539/Gucci_duffle_bag_mnxckr.jpg', category='Best Selling'),
        Product(name='RGB liquid CPU Cooler', description='Efficient CPU cooling solution.', price=1600, oldPrice=2000, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569539/RGB_liquid_CPU_Cooler_fkvlyj.jpg', category='Best Selling'),
        Product(name='Small BookShelf', description='Compact bookshelf for small spaces.', price=36210, oldPrice=42846, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569539/Small_BookShelf_gnmuyx.jpg', category='Best Selling'),
        Product(name='Breed Dry Dog Food', description='Nutritious dry dog food.', price=1030, oldPrice=1200, stock=100, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569538/Breed_Dry_Dog_Food_xwdpz9.jpg', category='Explore Products'),
        Product(name='CANON EOS DSLR Camera', description='High-quality DSLR camera.', price=3670, oldPrice=4350, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569531/CANON_EOS_DSLR_Camera_op1fa8.jpg', category='Explore Products'),
    ]

    # Women's Fashion
    womens_fashion_products = [
        Product(name='Elegant Evening Dress', description='Beautiful evening dress for special occasions.', price=8578, oldPrice=10503, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965422/Elegant_evening_dress_ffxalp.webp', category="Women's Fashion"),
        Product(name='Designer Handbag', description='Premium quality designer handbag.', price=10499, oldPrice=15000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965421/Designer_Handbag_vsblxj.webp', category="Women's Fashion"),
        Product(name='Summer Floral Dress', description='Light and comfortable floral dress for summer.', price=3500, oldPrice=4200, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965421/Summer_Floral_Dress_pry3vj.webp', category="Women's Fashion"),
    ]

    # Men's Fashion
    mens_fashion_products = [
        Product(name='Business Suit', description='Professional business suit for formal occasions.', price=13990, oldPrice=18232, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965420/Business_Suit_d52kcu.webp', category="Men's Fashion"),
        Product(name='Leather Jacket', description='Stylish leather jacket for casual wear.', price=8500, oldPrice=10000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965420/Leather_Jacket_whxuuc.webp', category="Men's Fashion"),
        Product(name='Apple Watch Ultra 2', description='Luxury wristwatch with precision movement.', price=21000, oldPrice=30100, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965419/Apple_Watch_Ultra_r9etoh.webp', category="Men's Fashion"),
    ]

    # Electronics 
    electronics_products = [
        Product(name='P9 Bluetooth Headphones', description='Portable Bluetooth headphones with noise cancellation.', price=1240, oldPrice=2800, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/P9_Bluetooth_headphones_cgz7am.webp', category='Electronics'),
        Product(name='Hisense 66 Inch Smart TV', description='4K Ultra HD Smart TV with voice control.', price=45000, oldPrice=55000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/Hisense_55_Inch_Smart_Tv_djjtpj.webp', category='Electronics'),
        Product(name='Canon EOS DSLR Camera', description='Professional DSLR camera with 24MP sensor.', price=35000, oldPrice=42000, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/Canon_Eos_200d_Dlsr_txjhpy.webp', category='Electronics'),
    ]

    # Combine all products
    all_products = original_products + womens_fashion_products + mens_fashion_products + electronics_products

    db.session.add_all(all_products)
    db.session.commit()

    # Add reviews - ensuring each user-product combination is unique
    # Create a set to track user-product combinations that have been reviewed
    reviewed_combinations = set()
    
    # Get all product IDs
    product_ids = [product.id for product in all_products]
    user_ids = [1, 2]  # Corresponds to 'alice' and 'bob' in auth service
    
    # Shuffle product IDs to get random distribution
    random.shuffle(product_ids)
    
    # Add reviews for a subset of products to avoid constraint violations
    for i in range(min(10, len(product_ids))):
        # Alternate between users
        user_id = user_ids[i % len(user_ids)]
        product_id = product_ids[i]
        
        # Check if this combination has already been reviewed
        if (user_id, product_id) not in reviewed_combinations:
            review = Review(
                user_id=user_id,
                product_id=product_id,
                rating=random.randint(3, 5),
                review_text=f"This is a great product! I really enjoy using it. Rating: {random.randint(3, 5)}/5"
            )
            db.session.add(review)
            reviewed_combinations.add((user_id, product_id))
    
    # Add some favorites
    for i in range(min(5, len(product_ids))):
        user_id = user_ids[i % len(user_ids)]
        product_id = product_ids[i]
        
        favorite = Favorite(
            user_id=user_id,
            product_id=product_id
        )
        db.session.add(favorite)
    
    db.session.commit()
    print("Product service database seeded successfully.")
