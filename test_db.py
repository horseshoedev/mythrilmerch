#!/usr/bin/env python3
"""
Test script to verify Neon database connection and show products
"""

import os
import psycopg2
from psycopg2 import Error
import json

def test_database():
    """Test database connection and show products"""
    db_url = os.environ.get("NETLIFY_DB_URL")
    
    if not db_url:
        print("❌ NETLIFY_DB_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to Neon database!")
        
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, price, image_url FROM products ORDER BY id")
        rows = cur.fetchall()
        
        print(f"\n📦 Found {len(rows)} products in database:")
        print("=" * 60)
        
        for row in rows:
            product = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "imageUrl": row[4]
            }
            print(f"ID: {product['id']}")
            print(f"Name: {product['name']}")
            print(f"Price: ${product['price']:.2f}")
            print(f"Description: {product['description'][:100]}...")
            print(f"Image: {product['imageUrl']}")
            print("-" * 40)
        
        cur.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MythrilMerch Database Connection")
    print("=" * 50)
    
    if test_database():
        print("\n🎉 Database test completed successfully!")
        print("\n💡 Your products are ready to be displayed in the frontend.")
    else:
        print("\n❌ Database test failed.") 