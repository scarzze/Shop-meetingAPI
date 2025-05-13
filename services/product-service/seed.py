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
        Product(name='ASUS F10 Gaming Laptop', description='Powerful gaming laptop.', price=7300, oldPrice=8550, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569531/ASUS_F10_Gaming_Laptop_trfaau.jpg', category='Explore Products'),
        Product(name='Curology Product Set', description='Complete skincare product set.', price=4855, oldPrice=6001, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569530/Curology_Product_Set_ujfhwx.avif', category='Explore Products'),
        Product(name='Kids Electric Car', description='Fun electric car for kids.', price=9607, oldPrice=11907, stock=5, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569531/Kids_Electric_Car_td4hss.webp', category='Explore Products'),
        Product(name='Jr. Zoom Soccer Cleats', description='High-performance soccer cleats.', price=7669, oldPrice=14000, stock=8, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569530/Jr._Zoom_Soccer_Cleats_gyera1.jpg', category='Explore Products'),
        Product(name='GP11 Shooter USB Gamepad', description='USB gamepad for gaming.', price=6240, oldPrice=7500, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569529/GP11_Shooter_USB_Gamepad_doahfk.jpg', category='Explore Products'),
        Product(name='Quilted Satin Jacket', description='Elegant satin jacket.', price=6995, oldPrice=8000, stock=12, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569530/Quilted_Satin_Jacket_svyu2c.jpg', category='Explore Products'),
        Product(name='PlayStation 5', description='Next-gen gaming console.', price=47912, oldPrice=55999, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569529/ps5_cordbj.jpg', category='New Arrivals'),
        Product(name="Women's Collections", description='Exclusive women fashion collections.', price=12428, oldPrice=18700, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746569530/womencollection_jiqros.webp', category='New Arrivals'),
    ]

    # Women's Fashion
    womens_fashion_products = [
        Product(name='Elegant Evening Dress', description='Beautiful evening dress for special occasions.', price=8578, oldPrice=10503, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965422/Elegant_evening_dress_ffxalp.webp', category="Women's Fashion"),
        Product(name='Designer Handbag', description='Premium quality designer handbag.', price=10499, oldPrice=15000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965421/Designer_Handbag_vsblxj.webp', category="Women's Fashion"),
        Product(name='Summer Floral Dress', description='Light and comfortable floral dress for summer.', price=3500, oldPrice=4200, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965421/Summer_Floral_Dress_pry3vj.webp', category="Women's Fashion"),
        Product(name='Red Stiletto Peep Toe High Heels', description='Elegant high heel shoes for formal occasions.', price=4500, oldPrice=5503, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965421/Red_stilleto_high_heels_xmfdwx.webp', category="Women's Fashion"),
        Product(name='Cashmere Sweater', description='Soft and warm cashmere sweater for winter.', price=6000, oldPrice=7549, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965420/Cashmere_sweater_kqeawr.webp', category="Women's Fashion"),
    ]

    # Men's Fashion
    mens_fashion_products = [
        Product(name='Business Suit', description='Professional business suit for formal occasions.', price=13990, oldPrice=18232, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965420/Business_Suit_d52kcu.webp', category="Men's Fashion"),
        Product(name='Leather Jacket', description='Stylish leather jacket for casual wear.', price=8500, oldPrice=10000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965420/Leather_Jacket_whxuuc.webp', category="Men's Fashion"),
        Product(name='Apple Watch Ultra 2', description='Luxury wristwatch with precision movement.', price=21000, oldPrice=30100, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965419/Apple_Watch_Ultra_r9etoh.webp', category="Men's Fashion"),
        Product(name='Casual Denim Jeans', description='Comfortable denim jeans for everyday wear.', price=790, oldPrice=990, stock=50, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965419/Casual_denim_jeans_i7tusl.webp', category="Men's Fashion"),
        Product(name='Oxford Dress Shoes', description='Classic Oxford dress shoes for formal occasions.', price=7500, oldPrice=9000, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965419/Oxford_dress_shoes_vd8nyw.webp', category="Men's Fashion"),
    ]

    # Electronics 
    electronics_products = [
        Product(name='P9 Bluetooth Headphones', description='Portable Bluetooth headphones with noise cancellation.', price=1240, oldPrice=2800, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/P9_Bluetooth_headphones_cgz7am.webp', category='Electronics'),
        Product(name='Hisense 66 Inch Smart TV', description='4K Ultra HD Smart TV with voice control.', price=45000, oldPrice=55000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/Hisense_55_Inch_Smart_Tv_djjtpj.webp', category='Electronics'),
        Product(name='Canon EOS DSLR Camera', description='Professional DSLR camera with 24MP sensor.', price=35000, oldPrice=42000, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965418/Canon_Eos_200d_Dlsr_txjhpy.webp', category='Electronics'),
        Product(name='Xiaomi Mi Portable Pocket Speaker', description='Portable Bluetooth speaker with 20-hour battery life.', price=3152, oldPrice=3500, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965417/Xiaomi_Mi_Portable_Pocket_Speaker_zxgc0f.webp', category='Electronics'),
        Product(name='HP Elitebook Revolve 810', description='10-inch tablet with high-resolution display.', price=17500, oldPrice=32000, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965417/HP_Elitebook_Revolve_810_dzsuu8.webp', category='Electronics'),
    ]

    # Home & Lifestyle 
    home_lifestyle_products = [
        Product(name='Sinbo Coffee Maker', description='Programmable coffee maker with thermal carafe.', price=5510, oldPrice=6500, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965417/Sinbo_Coffee_Maker_pt6r1b.webp', category='Home & Lifestyle'),
        Product(name='Luxury Bedding Set', description='Premium quality bedding set with duvet cover and pillowcases.', price=7010, oldPrice=8500, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965416/Luxury_Bedding_Set_otzb3n.webp', category='Home & Lifestyle'),
        Product(name='Tuya Smart Home Hub', description='Central hub for controlling all your smart home devices.', price=7025, oldPrice=9490, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965416/Tuya_Smart_Home_Hub_k9gfvp.webp', category='Home & Lifestyle'),
        Product(name='Decorative Wall Art', description='Beautiful wall art to enhance your home decor.', price=2330, oldPrice=3000, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965415/Decorative_Wall_Art_zezjhm.webp', category='Home & Lifestyle'),
        Product(name='9 pcs Kitchen Knives Set', description='Professional-grade kitchen knives set with wooden block.', price=3257, oldPrice=4809, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965415/Kitchen_knives_set_widwxd.webp', category='Home & Lifestyle'),
    ]

    # Medicine
    medicine_products = [
        Product(name='Universal Car Emergency Kit', description='Universal car emergency kit for car accidents.', price=2500, oldPrice=3000, stock=50, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965415/Universal_Car_Emergency_Kit_qbvv8n.webp', category='Medicine'),
        Product(name='Digital Thermometer', description='Accurate digital thermometer for temperature measurement.', price=1500, oldPrice=1800, stock=60, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965414/Non-Contact_Digital_Thermometer_tso40l.webp', category='Medicine'),
        Product(name='Blood Pressure Monitor', description='Home blood pressure monitor with digital display.', price=4500, oldPrice=5200, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965414/Blood_Pressure_Monitor_oyzpjx.jpg', category='Medicine'),
        Product(name='Vitamin Supplement Pack', description='Complete vitamin supplement pack for daily health.', price=3000, oldPrice=3600, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965413/Vitamin_Supplement_Pack_qekrjd.jpg', category='Medicine'),
        Product(name='Pain Relief Patches', description='Effective pain relief patches for muscle and joint pain.', price=1200, oldPrice=1500, stock=70, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965413/Pain_Relief_Patches_hbm1v4.jpg', category='Medicine'),
    ]

    # Sports & Outdoor 
    sports_outdoor_products = [
        Product(name='Yoga Mat', description='Non-slip yoga mat for home and studio practice.', price=2000, oldPrice=2400, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965413/Yoga_Mat_rtis0z.webp', category='Sports & Outdoor'),
        Product(name='HHII Black - 30 Speed Mountain Bike', description='Durable mountain bike for off-road adventures.', price=35000, oldPrice=42000, stock=10, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746966851/HHII_Black_-_30_Speed_Mountain_Bike_bqjodn.jpg', category='Sports & Outdoor'),
        Product(name='ADIDAS Tennis Racket', description='Professional tennis racket with carrying case.', price=5500, oldPrice=6800, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965413/ADIDAS_Tennis_Racket_dos9om.webp', category='Sports & Outdoor'),
        Product(name='Camping Tent upto 4 people', description='Waterproof camping tent for 4 persons.', price=6000, oldPrice=7200, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965413/Camping_Tent_upto_4_people_u1geiv.webp', category='Sports & Outdoor'), 
    ]

    # Baby's & Toys
    babies_toys_products = [
        Product(name='Baby Stroller', description='Lightweight and foldable baby stroller.', price=12000, oldPrice=15000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965411/Baby_stroller_slrirt.webp', category="Baby's & Toys"),
        Product(name='Montessori Wooden Educational Toy Set', description='Interactive educational toy set for early development.', price=1422, oldPrice=1822, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Montessori_Wooden_Education_Toy_gxxluh.webp', category="Baby's & Toys"),
        Product(name='PTZ Baby Monitor WiFi Camera', description='Digital baby monitor with video and audio.', price=5500, oldPrice=6500, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/PTZ_Baby_Monitor_WiFi_Camera_zavptf.webp', category="Baby's & Toys"),
        Product(name='Plush Teddy Bear', description='Soft and cuddly teddy bear for children.', price=390, oldPrice=500, stock=50, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Plush_Tedy_Bear_z5queu.webp', category="Baby's & Toys"),
        Product(name='Building Blocks Set', description='Creative building blocks set for children.', price=2500, oldPrice=3069, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Building_Blocks_Set_mlwoop.webp', category="Baby's & Toys"),
    ]

    # Groceries & Pets 
    groceries_pets_products = [
        Product(name='Organic Coffee Beans', description='Premium organic coffee beans, 500g pack.', price=1600, oldPrice=2200, stock=50, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Organic_Coffee_Beans_eetlg1.webp', category='Groceries & Pets'),
        Product(name='Ferplast Atlas 40 Pet Carrier', description='Comfortable pet carrier for small to medium pets.', price=4500, oldPrice=5500, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Ferplast_Atlas_40_Pet_Carrier_zwvt8o.webp', category='Groceries & Pets'),
        Product(name='Dog Food Premium', description='High-quality dog food for adult dogs, 5kg bag.', price=3450, oldPrice=4200, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Dog_Food_Premium_i4ksrt.webp', category='Groceries & Pets'),
        Product(name='54inCat Tree', description='Multi-level cat tree with scratching posts.', price=6456, oldPrice=7870, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/54in_Cat_Tree_g5ldk8.webp', category='Groceries & Pets'),
        Product(name='Gourmet Chocolate Box', description='Assorted gourmet chocolates in gift box.', price=2375, oldPrice=3000, stock=40, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Gourmet_Chocolate_Box_it5ism.webp', category='Groceries & Pets'),
    ]

    # Health & Beauty 
    health_beauty_products = [
        Product(name='Spirit of Kings - Nobility Perfume', description='Designer luxury perfume, 100ml bottle.', price=8440, oldPrice=10500, stock=20, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965410/Spirit_of_Kings_-_Nobility_Perfume_n7whkv.webp', category='Health & Beauty'),
        Product(name='Garnier Pure Active Intensive Charcoal 3 in 1 - 150 ml', description='Intensive charcoal 3 in 1 FaceWash', price=890, oldPrice=1999, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Garnier_Pure_Active_t1ju9w.webp', category='Health & Beauty'),
        Product(name='Oraimo SmartDent C2', description='Advanced electric toothbrush with multiple cleaning modes.', price=2799, oldPrice=3581, stock=30, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Oraimo_SmartDent_asymig.webp', category='Health & Beauty'),
        Product(name='12Pcs Professional Blow Dry Set', description='Professional hair styling kit with dryer and attachments.', price=7500, oldPrice=9000, stock=15, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Hair_Styling_Kit_ylsju6.webp', category='Health & Beauty'),
        Product(name='190 Colors Makeup Palette', description='Premium makeup palette with eyeshadows and blushes.', price=5831, oldPrice=7000, stock=25, image_url='https://res.cloudinary.com/dyzqn2sju/image/upload/v1746965409/Makeup_Palette_icn0al.webp', category='Health & Beauty'),
    ]

    # Combine all products
    all_products = original_products + womens_fashion_products + mens_fashion_products + electronics_products + home_lifestyle_products + medicine_products + sports_outdoor_products + babies_toys_products + groceries_pets_products + health_beauty_products

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
