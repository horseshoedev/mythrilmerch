#!/usr/bin/env python3
"""
Database setup script for MythrilMerch
This script helps initialize the database and run migrations.
"""

import os
import psycopg2
from psycopg2 import Error
import sys

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        # Try Netlify DB URL first (for production)
        db_url = os.environ.get("NETLIFY_DB_URL")
        if db_url:
            return psycopg2.connect(db_url)
        
        # Fall back to individual environment variables
        host = os.environ.get("DB_HOST", "localhost")
        database = os.environ.get("DB_NAME", "ecommerce_db")
        user = os.environ.get("DB_USER", "ecommerce_user")
        password = os.environ.get("DB_PASSWORD", "your_strong_password")
        
        return psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def run_migration(conn, migration_file):
    """Run a SQL migration file"""
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        print(f"✅ Successfully ran migration: {migration_file}")
        return True
    except Error as e:
        print(f"❌ Error running migration {migration_file}: {e}")
        conn.rollback()
        return False

def check_tables_exist(conn):
    """Check if required tables exist"""
    required_tables = ['products', 'cart_items', 'users', 'orders', 'order_items']
    existing_tables = []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        existing_tables = [table[0] for table in tables]
        cur.close()
    except Error as e:
        print(f"Error checking tables: {e}")
        return False
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    else:
        print("✅ All required tables exist")
        return True

def insert_sample_data(conn):
    """Insert sample products if they don't exist"""
    sample_products = [
        ('Mythril T-Shirt', 'Premium cotton t-shirt with Mythril logo', 29.99, 'https://example.com/mythril-tshirt.jpg'),
        ('Mythril Hoodie', 'Comfortable hoodie with embroidered Mythril design', 49.99, 'https://example.com/mythril-hoodie.jpg'),
        ('Mythril Mug', 'Ceramic mug with Mythril branding', 12.99, 'https://example.com/mythril-mug.jpg'),
        ('Mythril Sticker Pack', 'Set of 5 high-quality vinyl stickers', 8.99, 'https://example.com/mythril-stickers.jpg')
    ]
    
    try:
        cur = conn.cursor()
        for name, description, price, image_url in sample_products:
            cur.execute("""
                INSERT INTO products (name, description, price, image_url) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (name, description, price, image_url))
        conn.commit()
        cur.close()
        print("✅ Sample products inserted successfully")
        return True
    except Error as e:
        print(f"❌ Error inserting sample data: {e}")
        conn.rollback()
        return False

def main():
    """Main setup function"""
    print("🚀 MythrilMerch Database Setup")
    print("=" * 40)
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    print("✅ Database connection successful")
    
    # Check if tables exist
    if check_tables_exist(conn):
        print("Database schema already exists")
    else:
        print("Setting up database schema...")
        migration_file = "db/migrations/001_initial_schema.sql"
        
        if os.path.exists(migration_file):
            if run_migration(conn, migration_file):
                print("✅ Database schema created successfully")
            else:
                print("❌ Failed to create database schema")
                conn.close()
                sys.exit(1)
        else:
            print(f"❌ Migration file not found: {migration_file}")
            conn.close()
            sys.exit(1)
    
    # Insert sample data
    print("\n📦 Inserting sample products...")
    insert_sample_data(conn)
    
    # Verify setup
    print("\n🔍 Verifying setup...")
    if check_tables_exist(conn):
        print("✅ Database setup completed successfully!")
    else:
        print("❌ Database setup verification failed")
    
    conn.close()
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    main() 