# mythrilmerch-frontend/netlify/functions/api/main.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import Error
import os # Import os to access environment variables

app = Flask(__name__)
# Enable CORS for all routes. This is crucial for your React frontend
# running on a different origin (even a different port locally, or Netlify's domain online)
# to communicate with your Netlify Function.
CORS(app)

# Database Configuration - NOW USING ENVIRONMENT VARIABLES
# Netlify will inject NETLIFY_DB_URL, which contains the full connection string.
DATABASE_URL = os.environ.get("NETLIFY_DB_URL")

# Function to establish database connection
def get_db_connection():
    conn = None
    if not DATABASE_URL:
        # This print will appear in your Netlify Function logs if the variable isn't set
        print("NETLIFY_DB_URL environment variable not set. Cannot connect to database.")
        return None
    try:
        # Connect using the full connection string from the environment variable
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection successful (via Netlify DB URL)")
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

# API endpoint to add a product to the cart (now persistent in DB)
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        # Check if the product already exists in the cart
        cur.execute("SELECT id, quantity FROM cart_items WHERE product_id = %s;", (product_id,))
        existing_item = cur.fetchone()

        if existing_item:
            # If exists, update the quantity
            new_quantity = existing_item[1] + quantity
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s;", (new_quantity, existing_item[0]))
            message = "Product quantity updated in cart."
        else:
            # If not exists, insert new item
            cur.execute("INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s);", (product_id, quantity))
            message = "Product added to cart."

        conn.commit() # Commit the transaction to save changes to the database
        cur.close()
        return jsonify({"message": message}), 200
    except Error as e:
        conn.rollback() # Rollback in case of error to prevent partial updates
        print(f"Error adding/updating cart item: {e}")
        return jsonify({"error": "Error processing cart item"}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to get all items in the cart (now fetched from DB)
@app.route('/api/cart', methods=['GET'])
def get_cart():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cart_items = []
    try:
        cur = conn.cursor()
        # Join cart_items with products to get product details for display
        cur.execute("""
            SELECT
                ci.id AS cart_item_id,
                ci.product_id,
                ci.quantity,
                p.name,
                p.description,
                p.price,
                p.image_url
            FROM
                cart_items ci
            JOIN
                products p ON ci.product_id = p.id;
        """)
        rows = cur.fetchall()
        for row in rows:
            cart_items.append({
                "cartItemId": row[0],
                "productId": row[1],
                "quantity": row[2],
                "name": row[3],
                "description": row[4],
                "price": float(row[5]),
                "imageUrl": row[6]
            })
        cur.close()
    except Error as e:
        print(f"Error fetching cart items: {e}")
        return jsonify({"error": "Error fetching cart items"}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(cart_items)

# API endpoint to remove an item from the cart
@app.route('/api/cart/remove/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart_items WHERE id = %s;", (cart_item_id,))
        if cur.rowcount == 0:
            conn.rollback() # Rollback if no row was deleted
            return jsonify({"message": "Cart item not found"}), 404
        conn.commit()
        cur.close()
        return jsonify({"message": "Cart item removed successfully"}), 200
    except Error as e:
        conn.rollback()
        print(f"Error removing cart item: {e}")
        return jsonify({"error": "Error removing cart item"}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to update the quantity of a cart item
@app.route('/api/cart/update/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    data = request.get_json()
    new_quantity = data.get('quantity')

    if not isinstance(new_quantity, int) or new_quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s;", (new_quantity, cart_item_id))
        if cur.rowcount == 0:
            conn.rollback() # Rollback if no row was updated
            return jsonify({"message": "Cart item not found"}), 404
        conn.commit()
        cur.close()
        return jsonify({"message": "Cart item updated successfully"}), 200
    except Error as e:
        conn.rollback()
        print(f"Error updating cart item: {e}")
        return jsonify({"error": "Error updating cart item"}), 500
    finally:
        if conn:
            conn.close()

# This `app` instance is what Netlify's Python runtime will use.
# We don't need `if __name__ == '__main__': app.run(...)` here.
