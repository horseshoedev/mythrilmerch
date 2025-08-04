#!/usr/bin/env python3
"""
Add real product data to MythrilMerch Neon database
"""

import os
import psycopg2
from psycopg2 import Error

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        db_url = os.environ.get("NETLIFY_DB_URL")
        if db_url:
            return psycopg2.connect(db_url)
        else:
            print("❌ NETLIFY_DB_URL environment variable not set")
            return None
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def add_real_products():
    """Add real product data to the database"""
    products = [
        {
            'name': 'Mythril Gaming T-Shirt',
            'description': 'Premium cotton gaming t-shirt featuring the iconic Mythril logo. Perfect for gamers who want to show their style both in-game and out.',
            'price': 24.99,
            'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop'
        },
        {
            'name': 'Mythril Hoodie',
            'description': 'Comfortable and stylish hoodie with embroidered Mythril design. Made from high-quality cotton blend for maximum comfort during long gaming sessions.',
            'price': 49.99,
            'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop'
        },
        {
            'name': 'Mythril Gaming Mug',
            'description': 'Ceramic gaming mug with Mythril branding. Perfect for your morning coffee or late-night gaming sessions. Holds 12oz of your favorite beverage.',
            'price': 14.99,
            'image_url': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400&h=400&fit=crop'
        },
        {
            'name': 'Mythril Sticker Pack',
            'description': 'Set of 5 high-quality vinyl stickers featuring Mythril designs. Perfect for decorating your laptop, water bottle, or gaming setup.',
            'price': 8.99,
            'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop'
        },
        {
            'name': 'Mythril Gaming Mouse Pad',
            'description': 'Large gaming mouse pad with Mythril design. Non-slip rubber base with smooth cloth surface for precise mouse control.',
            'price': 19.99,
            'image_url': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400&h=400&fit=crop'
        },
        {
            'name': 'Mythril Gaming Headset',
            'description': 'High-quality gaming headset with Mythril branding. Features noise-cancelling microphone and immersive sound for the ultimate gaming experience.',
            'price': 79.99,
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop'
        }
    ]
    
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cur = conn.cursor()
        
        # Clear existing products
        cur.execute("DELETE FROM products")
        print("🗑️  Cleared existing products")
        
        # Insert new products
        for product in products:
            cur.execute("""
                INSERT INTO products (name, description, price, image_url) 
                VALUES (%s, %s, %s, %s)
            """, (product['name'], product['description'], product['price'], product['image_url']))
            print(f"✅ Added: {product['name']}")
        
        conn.commit()
        cur.close()
        print(f"\n🎉 Successfully added {len(products)} products to the database!")
        return True
        
    except Error as e:
        print(f"❌ Error adding products: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def test_api_connection():
    """Test if the API can connect to the database"""
    print("\n🔍 Testing API connection...")
    
    # Test database connection directly
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM products")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            print(f"✅ Database connection successful - {count} products found")
            return True
        except Error as e:
            print(f"❌ Database query failed: {e}")
            return False
    else:
        print("❌ Database connection failed")
        return False

if __name__ == "__main__":
    print("🚀 MythrilMerch Product Setup")
    print("=" * 40)
    
    if test_api_connection():
        print("\n📦 Adding real product data...")
        if add_real_products():
            print("\n🎉 Product setup completed successfully!")
            print("\n💡 Your products are now available in the database.")
            print("   The frontend should automatically load them when you refresh the page.")
        else:
            print("\n❌ Failed to add products")
    else:
        print("\n❌ Cannot proceed without database connection") 