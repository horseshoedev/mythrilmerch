from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import Error
import os # Import the os module to access environment variables

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Database Configuration: Use environment variables for production
# IMPORTANT: Set these environment variables in your deployment environment (e.g., system, Docker, cloud platform)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "ecommerce_db")
DB_USER = os.environ.get("DB_USER", "ecommerce_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "your_strong_password") # <<< CHANGE THE DEFAULT to your actual password!

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
        # Check if the product already exists in the cart for the current user (assuming no user ID for now)
        cur.execute("SELECT id, quantity FROM cart_items WHERE product_id = %s;", (product_id,))
        existing_item = cur.fetchone()

        if existing_item:
            new_quantity = existing_item[1] + quantity
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s;", (new_quantity, existing_item[0]))
            message = "Product quantity updated in cart."
        else:
            cur.execute("INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s);", (product_id, quantity))
            message = "Product added to cart."

        conn.commit()
        cur.close()
        return jsonify({"message": message}), 200
    except Error as e:
        conn.rollback() # Rollback in case of error
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

    cart_items_data = [] # Renamed to avoid conflict with former in-memory list
    try:
        cur = conn.cursor()
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
            cart_items_data.append({
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
    return jsonify(cart_items_data)

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
            conn.rollback()
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
            conn.rollback()
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

# Run the Flask app
if __name__ == '__main__':
    # Use environment variable for debug mode, default to False for safety
    # In a production environment, ensure FLASK_DEBUG is not set or set to '0'
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)