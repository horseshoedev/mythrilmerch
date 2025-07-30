#!/usr/bin/env python3
"""
Neon Database Setup for MythrilMerch
This script helps configure and test the Neon database connection.
"""

import os
import psycopg2
from psycopg2 import Error
import sys

def test_neon_connection(db_url):
    """Test connection to Neon database"""
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to Neon database!")
        conn.close()
        return True
    except Error as e:
        print(f"❌ Failed to connect to Neon: {e}")
        return False

def setup_neon():
    """Interactive setup for Neon database"""
    print("🚀 MythrilMerch Neon Database Setup")
    print("=" * 40)
    
    # Check if NETLIFY_DB_URL is already set
    db_url = os.environ.get("NETLIFY_DB_URL")
    
    if not db_url:
        print("\n📋 Please provide your Neon database URL.")
        print("You can find this in your Neon dashboard under 'Connection Details'")
        print("It should look like: postgresql://username:password@hostname/database")
        print()
        
        db_url = input("Enter your Neon database URL: ").strip()
        
        if not db_url:
            print("❌ No database URL provided. Exiting.")
            return False
        
        # Set the environment variable for this session
        os.environ["NETLIFY_DB_URL"] = db_url
        print("✅ Database URL set for this session")
    
    # Test the connection
    print("\n🔍 Testing database connection...")
    if not test_neon_connection(db_url):
        return False
    
    # Run the database setup
    print("\n📦 Setting up database schema...")
    try:
        from db.setup import main as setup_main
        setup_main()
        return True
    except ImportError:
        print("❌ Could not import setup module. Make sure you're in the correct directory.")
        return False

if __name__ == "__main__":
    if setup_neon():
        print("\n🎉 Neon database setup completed successfully!")
        print("\n💡 To make this permanent, add to your shell profile:")
        print(f"export NETLIFY_DB_URL='your_neon_url_here'")
    else:
        print("\n❌ Setup failed. Please check your Neon database URL and try again.")
        sys.exit(1) 