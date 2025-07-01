# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import Error

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Database Configuration
# IMPORTANT: Replace these with your PostgreSQL database credentials
# created in Step 1.2. For a real application, use environment variables!
DB_HOST = "localhost"
DB_NAME = "ecommerce_db"
DB_USER = "ecommerce_user"
DB_PASSWORD = "your_password" # <<< CHANGE THIS to your actual password!

# Function to establish database connection
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Database connection successful")
    except Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
    return conn

# API Endpoint to get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    products = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, price, image_url FROM products;")
        rows = cur.fetchall()
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]), # Convert Decimal to float for JSON serialization
                "imageUrl": row[4] # Consistent camelCase for frontend
            })
        cur.close()
    except Error as e:
        print(f"Error fetching products: {e}")
        return jsonify({"error": "Error fetching products"}), 500
    finally:
        if conn:
            conn.close()
            print("Database connection closed")
    return jsonify(products)

# test
# Simple API endpoint for adding to cart (in-memory for this demo)
# In a real application, this would involve user sessions and a database cart.
cart_items = [] # This will reset every time the server restarts

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('productId')
    quantity = data.get('quantity', 1) # Default to 1 if not provided

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    # In a real app, you'd fetch product details from DB using product_id
    # For this demo, we'll just add the ID and quantity
    cart_items.append({"productId": product_id, "quantity": quantity})
    print(f"Added product {product_id} to cart. Current cart: {cart_items}")
    return jsonify({"message": "Product added to cart", "cartItems": cart_items}), 200

@app.route('/api/cart', methods=['GET'])
def get_cart():
    return jsonify(cart_items)


# Run the Flask app
if __name__ == '__main__':
    # You can specify the host and port here.
    # host='0.0.0.0' makes it accessible from other machines on your network,
    # useful if testing on different devices or a Docker setup.
    # debug=True allows for automatic reloading on code changes and provides
    # a debugger, but should NEVER be used in production.
    app.run(host='127.0.0.1', port=5000, debug=True)
