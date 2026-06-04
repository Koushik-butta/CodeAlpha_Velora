import os
import sys

# Force using development settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'velora.settings.dev')

sys.path.append(os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Category, Product, ProductImage
from django.utils.text import slugify

User = get_user_model()

def seed_products():
    print("Starting comprehensive product database seeding...")

    # 1. Ensure categories are created/active
    Category.get_all_active()
    
    # Cache categories by slug
    categories = {cat.slug: cat for cat in Category.objects.all()}
    print(f"Loaded {len(categories)} active categories.")

    # 2. Setup user sellers
    sellers_data = [
        {'email': 'karan.grover@gmail.com', 'name': 'Karan Grover', 'city': 'Delhi', 'state': 'Delhi NCR'},
        {'email': 'priya.sharma@gmail.com', 'name': 'Priya Sharma', 'city': 'Bengaluru', 'state': 'Karnataka'},
        {'email': 'rahul.mehta@gmail.com', 'name': 'Rahul Mehta', 'city': 'Mumbai', 'state': 'Maharashtra'},
        {'email': 'ananya.sen@gmail.com', 'name': 'Ananya Sen', 'city': 'Pune', 'state': 'Maharashtra'},
        {'email': 'akash.patel@gmail.com', 'name': 'Akash Patel', 'city': 'Hyderabad', 'state': 'Telangana'},
        {'email': 'official.stores@velora.in', 'name': 'Velora Official Brand Store', 'city': 'Mumbai', 'state': 'Maharashtra'},
    ]

    sellers = {}
    for s in sellers_data:
        user, created = User.objects.get_or_create(email=s['email'])
        if created:
            user.set_password('password123')
            user.is_active = True
            user.save()
            print(f"Created user account: {user.email}")
        
        # Sync profile details
        profile = user.profile
        profile.full_name = s['name']
        profile.city = s['city']
        profile.state = s['state']
        profile.is_verified = True
        profile.save()
        
        sellers[s['email']] = user

    # Clear previous seed products to avoid duplicate conflicts if necessary,
    # or just use get_or_create. Let's use get_or_create by title to allow safely running the script multiple times.
    
    # 3. Define 30 Products (3 New + 3 Second Hand for each of the 5 categories)
    products_to_create = [
        # === 1. MOBILES ===
        # --- Brand New ---
        {
            'category_slug': 'mobiles',
            'seller_email': 'official.stores@velora.in',
            'title': 'Apple iPhone 17 Pro Max (256GB, Cosmic Orange)',
            'price': 149900,
            'original_price': 159900,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Apple',
            'model_name': 'iPhone 17 Pro Max',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': "Apple iPhone 17 Pro Max 256 GB. Features a 17.42 cm (6.9'') Display with ProMotion, A19 Pro Chip, Best Battery Life in Any iPhone Ever, Pro Fusion Camera System, and Center Stage Front Camera in Cosmic Orange color.",
            'image_url': '/static/img/iphone_17_pro_max.png',
        },
        {
            'category_slug': 'mobiles',
            'seller_email': 'official.stores@velora.in',
            'title': 'Samsung Galaxy S24 5G (Onyx Black, 128GB)',
            'price': 45000,
            'original_price': 74999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Samsung',
            'model_name': 'Galaxy S24',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Samsung Galaxy S24 Snapdragon 8 Gen 3 5G (Onyx Black, 128 GB) (8 GB RAM). Features dynamic AMOLED 2X screen, advanced AI camera enhancements, and long-lasting battery life. Under brand warranty.',
            'image_url': '/static/img/samsung_galaxy_s24.png',
        },
        {
            'category_slug': 'mobiles',
            'seller_email': 'official.stores@velora.in',
            'title': 'OnePlus 13R 5G (Nebula Noir, 12GB RAM, 256GB Storage)',
            'price': 39999,
            'original_price': 49999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'OnePlus',
            'model_name': '13R 5G',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'OnePlus 13R | Smarter with OnePlus AI (12GB RAM, 256GB Storage, Nebula Noir). Flagship power made smarter with Snapdragon 8 Gen 3, a massive 6000mAh Battery, and 80W SUPERVOOC charging.',
            'image_url': '/static/img/oneplus_13r.png',
        },
        # --- Second Hand / Pre-owned ---
        {
            'category_slug': 'mobiles',
            'seller_email': 'priya.sharma@gmail.com',
            'title': 'Apple iPhone 13 (Blue, 128GB Storage)',
            'price': 38499,
            'original_price': 59900,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'Apple',
            'model_name': 'iPhone 13',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Selling my pristine iPhone 13. Blue color, 128GB capacity. Battery health is at 90%. Always used with a Spigen case and tempered glass. Zero scratches or dents. Comes with original box and unused charging cable.',
            'image_url': 'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 38000,
            'exchange_for': 'iPhone 14 or Samsung Galaxy S23 (I will pay difference)',
        },
        {
            'category_slug': 'mobiles',
            'seller_email': 'rahul.mehta@gmail.com',
            'title': 'OnePlus 11R 5G (Galactic Silver, 128GB Storage)',
            'price': 24499,
            'original_price': 39999,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'OnePlus',
            'model_name': '11R 5G',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Selling my OnePlus 11R Galactic Silver. Phone is 10 months old and performs beautifully. Snapdragon 8+ Gen 1, excellent gaming performance. 100W charging works perfectly (charger included). Minor scratches on the plastic frame.',
            'image_url': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 24000,
            'exchange_for': 'iPad Air or gaming console',
        },
        {
            'category_slug': 'mobiles',
            'seller_email': 'akash.patel@gmail.com',
            'title': 'Samsung Galaxy S22 5G (Phantom Black, 128GB)',
            'price': 28999,
            'original_price': 72999,
            'listing_type': 'sell',
            'condition': 'fair',
            'brand': 'Samsung',
            'model_name': 'Galaxy S22',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'description': 'Selling Galaxy S22 in Phantom Black. Screen has small scuffs but no cracks. Performance is excellent. Battery health is around 82% (lasts a work day). Device only, no charger or box.',
            'image_url': 'https://images.unsplash.com/photo-1610792516307-ea5acd9c3b00?w=600&auto=format&fit=crop&q=80',
        },

        # === 2. LAPTOPS ===
        # --- Brand New ---
        {
            'category_slug': 'laptops',
            'seller_email': 'official.stores@velora.in',
            'title': 'Apple MacBook Air M3 (13-inch, 8GB Unified RAM, 256GB SSD)',
            'price': 104900,
            'original_price': 114900,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Apple',
            'model_name': 'MacBook Air M3',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'The Apple M3 chip makes the super-portable 13-inch MacBook Air even more capable. With up to 18 hours of battery life, you can take it anywhere and blaze through work and play. Brand new, sealed box.',
            'image_url': 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'laptops',
            'seller_email': 'official.stores@velora.in',
            'title': 'ASUS ROG Zephyrus G14 (AMD Ryzen 9, RTX 4060, 16GB RAM)',
            'price': 124999,
            'original_price': 149999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'ASUS',
            'model_name': 'ROG Zephyrus G14',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Incredible power in a compact 14-inch gaming laptop. Packs a Ryzen 9 7940HS CPU, NVIDIA GeForce RTX 4060 GPU, ROG Nebula Display (165Hz, QHD), and signature AniMe Matrix lid styling. Covered under ASUS brand warranty.',
            'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'laptops',
            'seller_email': 'official.stores@velora.in',
            'title': 'HP Pavilion 15 Core i5 (12th Gen, 16GB DDR4, 512GB SSD)',
            'price': 49999,
            'original_price': 59999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'HP',
            'model_name': 'Pavilion 15',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'HP Pavilion 15.6-inch laptop. Powered by Intel Core i5 12th Gen processor, with 16GB RAM and 512GB NVMe SSD. Dynamic styling with back-lit keyboard and numeric pad. Includes Windows 11 and MS Office pre-activated.',
            'image_url': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80',
        },
        # --- Second Hand / Pre-owned ---
        {
            'category_slug': 'laptops',
            'seller_email': 'karan.grover@gmail.com',
            'title': 'Dell XPS 13 9310 Intel Core i7 (16GB RAM, 512GB SSD)',
            'price': 44999,
            'original_price': 109999,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'Dell',
            'model_name': 'XPS 13 9310',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'Selling my Dell XPS 13. High-end configuration: Intel Core i7 11th Gen, 16GB LPDDR4x RAM, 512GB NVMe SSD, gorgeous InfinityEdge FHD+ screen. Minimalist, premium aluminum deck. Extremely clean, always kept on office desk.',
            'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'laptops',
            'seller_email': 'akash.patel@gmail.com',
            'title': 'ASUS ROG Strix G15 Core i7 Gaming Laptop',
            'price': 38000,
            'original_price': 84990,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'ASUS',
            'model_name': 'ROG Strix G15',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'description': 'ASUS ROG gaming laptop. Setup: Core i7 10th Gen, Nvidia GTX 1650 Ti, 16GB RAM, 512GB SSD. Great for esports titles like Valorant, CS2, GTA V. RGB keyboard is fully working. Selling because I bought a desktop.',
            'image_url': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 38000,
            'exchange_for': 'MacBook Air M1/M2 or iPhone 13 Pro',
        },
        {
            'category_slug': 'laptops',
            'seller_email': 'ananya.sen@gmail.com',
            'title': 'Lenovo ThinkPad L14 Business Laptop',
            'price': 19999,
            'original_price': 55000,
            'listing_type': 'sell',
            'condition': 'fair',
            'brand': 'Lenovo',
            'model_name': 'ThinkPad L14',
            'city': 'Pune',
            'state': 'Maharashtra',
            'description': 'Lenovo ThinkPad L14 Gen 1. Specs: Intel i5 10th Gen, 8GB RAM, 256GB SSD. Highly durable keyboard and build. Average battery backup is 3 hours. Keyboard displays keys slightly shiny but works perfectly.',
            'image_url': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format&fit=crop&q=80',
        },

        # === 3. ELECTRONICS / AUDIO ===
        # --- Brand New ---
        {
            'category_slug': 'electronics',
            'seller_email': 'official.stores@velora.in',
            'title': 'Sony WH-1000XM5 Wireless Noise Cancelling Headphones',
            'price': 26990,
            'original_price': 34990,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Sony',
            'model_name': 'WH-1000XM5',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Industry-leading noise cancelling wireless over-ear headphones with auto NC optimizer, crystal clear hands-free calling, and 30 hours battery backup. Brand new sealed item with bill and warranty card.',
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'electronics',
            'seller_email': 'official.stores@velora.in',
            'title': 'Apple AirPods Pro (2nd Generation) with MagSafe USB-C',
            'price': 20900,
            'original_price': 24900,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Apple',
            'model_name': 'AirPods Pro 2',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'AirPods Pro feature up to 2x more Active Noise Cancellation, plus Adaptive Audio and Transparency mode. Includes MagSafe Charging Case (USB-C) with speaker and lanyard loop. Under brand warranty.',
            'image_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'electronics',
            'seller_email': 'official.stores@velora.in',
            'title': 'Samsung Galaxy Watch 6 LTE (44mm, Graphite Smartwatch)',
            'price': 18999,
            'original_price': 29999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Samsung',
            'model_name': 'Galaxy Watch 6',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Galaxy Watch6 features cellular LTE connectivity, sleep coaching, detailed body composition analyzer, heart rate tracker, and a bigger display. Graphite aluminum case with matching band.',
            'image_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop&q=80',
        },
        # --- Second Hand / Pre-owned ---
        {
            'category_slug': 'electronics',
            'seller_email': 'karan.grover@gmail.com',
            'title': 'JBL Tune Beam 2 Active Noise Cancelling Earphones',
            'price': 2499,
            'original_price': 5499,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'JBL',
            'model_name': 'Tune Beam 2',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'JBL Tune Beam 2 wireless bluetooth earbuds. Deep bass signature sound with fully working active noise cancelling. Used for just 1 week. Comes with box, charger, extra tips, and purchase invoice.',
            'image_url': 'https://images.unsplash.com/photo-1608156639585-b3a032ef9689?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 2400,
            'exchange_for': 'Wireless mouse or mechanical keyboard',
        },
        {
            'category_slug': 'electronics',
            'seller_email': 'rahul.mehta@gmail.com',
            'title': 'Fire-Boltt Aero Smartwatch with BT Calling',
            'price': 1299,
            'original_price': 7999,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'Fire-Boltt',
            'model_name': 'Aero Smartwatch',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Selling my Fire-Boltt smartwatch. 1.9-inch HD display, bluetooth calling, voice assistant, heart tracking. 100% scratchless screen, looks completely brand new. Charging cable included.',
            'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'electronics',
            'seller_email': 'priya.sharma@gmail.com',
            'title': 'Sony WF-1000XM4 Noise Cancelling Earbuds',
            'price': 7499,
            'original_price': 19990,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'Sony',
            'model_name': 'WF-1000XM4',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Premium wireless Sony noise cancelling earbuds. Used for 1.5 years. Battery backup is around 4 hours with Active Noise Cancelling turned on. Foam ear tips replaced recently. Clear case included.',
            'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80',
        },

        # === 4. FASHION ===
        # --- Brand New ---
        {
            'category_slug': 'fashion',
            'seller_email': 'official.stores@velora.in',
            'title': 'Nike Air Force 1 \'07 Triple White Sneakers',
            'price': 7495,
            'original_price': 9695,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Nike',
            'model_name': 'Air Force 1 \'07',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'The radiance lives on in the Nike Air Force 1 \'07, the basketball original that puts a fresh spin on what you know best: crisp leather, bold colors and the perfect amount of flash. 100% authentic, brand new in box.',
            'image_url': 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'fashion',
            'seller_email': 'official.stores@velora.in',
            'title': "Adidas Men's Clinch-X M Running Shoe",
            'price': 1729,
            'original_price': 3599,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Adidas',
            'model_name': 'Clinch-X M',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': "adidas Men's Clinch-X M Running Shoe. Features a lightweight, breathable mesh upper, signature 3-stripes side detailing, and high-traction sole for daily workout comfort. Original box pack.",
            'image_url': '/static/img/adidas_clinch_x_shoe.png',
        },
        {
            'category_slug': 'fashion',
            'seller_email': 'official.stores@velora.in',
            'title': "Levi's Men's 511 Slim Fit Jeans",
            'price': 1499,
            'original_price': 2999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': "Levi's",
            'model_name': '511 Slim',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': "Levi's Men's 511 Slim Fit Mid Rise Jeans. Premium stretch denim with standard 5-pocket styling. Perfect slim leg opening for casual wear. Brand new with tags.",
            'image_url': '/static/img/levis_511_jeans.png',
        },
        # --- Second Hand / Pre-owned ---
        {
            'category_slug': 'fashion',
            'seller_email': 'ananya.sen@gmail.com',
            'title': "USPA Men's Anton Stylish Casual Sneaker Shoe",
            'price': 1799,
            'original_price': 3599,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'USPA',
            'model_name': 'Anton Sneaker',
            'city': 'Pune',
            'state': 'Maharashtra',
            'description': "USPA U.S. Polo Assn. Men|Anton| Stylish Casual Sneaker Shoe. Tan brown sleek casual lifestyle sneaker. Lightly worn once, perfect like-new condition. Very comfortable foam inner lining.",
            'image_url': '/static/img/uspa_anton_sneaker.png',
            'exchange_available': True,
            'exchange_value_estimate': 1799,
            'exchange_for': 'Sneakers in UK Size 9.5 or premium backpack',
        },
        {
            'category_slug': 'fashion',
            'seller_email': 'priya.sharma@gmail.com',
            'title': 'Zara Oversized Corduroy Jacket (Black, Size M)',
            'price': 1999,
            'original_price': 4999,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'Zara',
            'model_name': 'Oversized Corduroy',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Black corduroy jacket from Zara. Button front closure, double chest pocket. Extremely comfortable and in clean like-new condition. Worn only 2 times.',
            'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'fashion',
            'seller_email': 'rahul.mehta@gmail.com',
            'title': 'Casio G-Shock Classic Analog-Digital Watch (GA-2100)',
            'price': 3499,
            'original_price': 6995,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'Casio',
            'model_name': 'G-Shock GA-2100',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'The famous "CasiOak" GA-2100 carbon core guard watch. All black tactical colorway. Resin strap showing minor signs of wear near the buckle. Glass is absolutely scratchless. Works perfectly.',
            'image_url': 'https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 3400,
            'exchange_for': 'Fossil or Seiko Chronograph watch',
        },

        # === 5. FURNITURE ===
        # --- Brand New ---
        {
            'category_slug': 'furniture',
            'seller_email': 'official.stores@velora.in',
            'title': 'Green Soul Jupiter Superb Ergonomic Mesh Office Chair',
            'price': 8990,
            'original_price': 18890,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Green Soul',
            'model_name': 'Jupiter Superb',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Green Soul Jupiter Superb | Ergonomic Mesh Office Chair for Work | 3 Year Warranty | Multi-Lock Synchro Tilt Recline Mechanism | 2D Armrest | Adjustable Lumbar | High Back | Grey color.',
            'image_url': '/static/img/green_soul_jupiter_chair.png',
        },
        {
            'category_slug': 'furniture',
            'seller_email': 'official.stores@velora.in',
            'title': 'Sleepwell Orthomed Single Bed Mattress (5-inch Memory Foam)',
            'price': 4999,
            'original_price': 7999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Sleepwell',
            'model_name': 'Orthomed Single',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Brand new Sleepwell orthopedic single bed mattress (72x36 inches, 5-inch thickness). Multi-layered high density memory foam core designed to relief back pressure and align the spine.',
            'image_url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'furniture',
            'seller_email': 'official.stores@velora.in',
            'title': 'Urban Ladder Solid Wood Coffee Table (Teak Finish)',
            'price': 8999,
            'original_price': 14999,
            'listing_type': 'buy',
            'condition': 'new',
            'brand': 'Urban Ladder',
            'model_name': 'Coffee Table',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'Solid Sheesham wood coffee table in warm teak finish. Elegant, simple box-frame styling with two under-drawers for storage. Perfect centerpiece for your premium living room. Covered under brand warranty.',
            'image_url': 'https://images.unsplash.com/photo-1581428982868-e410dd047a90?w=600&auto=format&fit=crop&q=80',
        },
        # --- Second Hand / Pre-owned ---
        {
            'category_slug': 'furniture',
            'seller_email': 'ananya.sen@gmail.com',
            'title': 'IKEA Micke Computer Desk (White, 105x50 cm)',
            'price': 3499,
            'original_price': 7990,
            'listing_type': 'sell',
            'condition': 'like_new',
            'brand': 'IKEA',
            'model_name': 'Micke Desk',
            'city': 'Pune',
            'state': 'Maharashtra',
            'description': 'Selling my white IKEA study desk. It has a built-in drawer, computer cable outlet, and adjustable shelving unit. Condition is excellent, very clean surface. Minor tape residue on the back edge.',
            'image_url': 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'furniture',
            'seller_email': 'karan.grover@gmail.com',
            'title': 'Sleepwell Orthopedic Single Bed Mattress (Pre-owned)',
            'price': 2499,
            'original_price': 6999,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'Sleepwell',
            'model_name': 'Orthomed Single',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'Used Sleepwell orthopedic single bed mattress. Soft memory foam feel. Very clean, absolutely no stains or odors. Upgrading to a double bed setup, hence selling this.',
            'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600&auto=format&fit=crop&q=80',
        },
        {
            'category_slug': 'furniture',
            'seller_email': 'akash.patel@gmail.com',
            'title': 'Solid Wooden Study Table with 3 Drawers',
            'price': 1899,
            'original_price': 4500,
            'listing_type': 'sell',
            'condition': 'good',
            'brand': 'Local Artisan',
            'model_name': 'Study Table',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'description': 'Sturdy wooden study/office desk with 3 sliding drawers. Very durable build, made of local rosewood. Shows slight surface wear but has no structurally weak points.',
            'image_url': 'https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=600&auto=format&fit=crop&q=80',
        },
        # === 6. EXCHANGE PRODUCTS ===
        {
            'category_slug': 'mobiles',
            'seller_email': 'rahul.mehta@gmail.com',
            'title': 'Google Pixel 10 Pro (Jade, 256GB, 16GB RAM)',
            'price': 108999,
            'original_price': 109999,
            'listing_type': 'exchange',
            'condition': 'like_new',
            'brand': 'Google',
            'model_name': 'Pixel 10 Pro',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'description': 'Looking to exchange my Google Pixel 10 Pro (Jade, 256 GB) (16 GB RAM). Brand new like condition, unused screen. Seeking equivalent iPhone 16 Pro or Samsung S24 Ultra in exchange.',
            'image_url': '/static/img/google_pixel_10_pro.png',
            'exchange_available': True,
            'exchange_value_estimate': 108999,
            'exchange_for': 'iPhone 16 Pro or Samsung Galaxy S24 Ultra',
        },
        {
            'category_slug': 'electronics',
            'seller_email': 'priya.sharma@gmail.com',
            'title': 'Sony WH-CH720N Wireless Over-Ear Headphones',
            'price': 5500,
            'original_price': 9990,
            'listing_type': 'exchange',
            'condition': 'good',
            'brand': 'Sony',
            'model_name': 'WH-CH720N',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'description': 'Looking to exchange my Sony WH-CH720N over-ear active noise cancelling headphones. Excellent sound quality and battery life. Looking for equivalent wireless earbuds (TWS) or a good smartwatch.',
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 5500,
            'exchange_for': 'Premium TWS Earbuds or Smartwatch',
        },
        {
            'category_slug': 'fashion',
            'seller_email': 'karan.grover@gmail.com',
            'title': 'Royal Enfield Classic Riding Jacket (Black, Size L)',
            'price': 4200,
            'original_price': 7500,
            'listing_type': 'exchange',
            'condition': 'like_new',
            'brand': 'Royal Enfield',
            'model_name': 'Classic Jacket',
            'city': 'Delhi',
            'state': 'Delhi NCR',
            'description': 'Royal Enfield mesh riding jacket with CE level 1 armor on elbows and shoulders. Worn for only 3 short rides. I gained some weight, so looking to exchange for a Size XL riding jacket of similar quality.',
            'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80',
            'exchange_available': True,
            'exchange_value_estimate': 4200,
            'exchange_for': 'Riding Jacket (Size XL) or equivalent riding boots',
        },
    ]

    for p in products_to_create:
        cat_slug = p.pop('category_slug')
        seller_email = p.pop('seller_email')
        img_url = p.pop('image_url')
        
        category = categories.get(cat_slug)
        seller = sellers.get(seller_email)
        
        if not category or not seller:
            print(f"Skipping product '{p['title']}' because category or seller was not resolved.")
            continue
            
        prod, created = Product.objects.get_or_create(
            title=p['title'],
            seller=seller,
            defaults={
                'category': category,
                'price': p['price'],
                'original_price': p['original_price'],
                'listing_type': p['listing_type'],
                'condition': p['condition'],
                'brand': p['brand'],
                'model_name': p['model_name'],
                'city': p['city'],
                'state': p['state'],
                'description': p['description'],
                'exchange_available': p.get('exchange_available', False),
                'exchange_value_estimate': p.get('exchange_value_estimate'),
                'exchange_for': p.get('exchange_for', ''),
                'is_active': True,
                'is_sold': False,
            }
        )
        
        if created:
            print(f"Created product: {prod.title}")
            ProductImage.objects.create(
                product=prod,
                image_url=img_url,
                is_primary=True,
                order=0
            )
        else:
            # Sync pricing/seller variables to ensure correctness in existing
            prod.price = p['price']
            prod.original_price = p['original_price']
            prod.condition = p['condition']
            prod.brand = p['brand']
            prod.model_name = p['model_name']
            prod.city = p['city']
            prod.state = p['state']
            prod.description = p['description']
            prod.listing_type = p['listing_type']
            prod.exchange_available = p.get('exchange_available', False)
            prod.exchange_value_estimate = p.get('exchange_value_estimate')
            prod.exchange_for = p.get('exchange_for', '')
            prod.save()
            print(f"Verified/Synced existing product: {prod.title}")
            
            # Sync image URL to ensure correct images are displayed
            primary_img = prod.images.filter(is_primary=True).first() or prod.images.first()
            if primary_img:
                primary_img.image_url = img_url
                primary_img.save()
                print(f"Updated primary image for product: {prod.title}")
            else:
                ProductImage.objects.create(
                    product=prod,
                    image_url=img_url,
                    is_primary=True,
                    order=0
                )

    print("Comprehensive database seeding complete.")

if __name__ == '__main__':
    seed_products()
