from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
from psycopg2 import Error
import os
import logging
from datetime import datetime
import ssl

# Import our modules
from auth import init_auth, UserService, create_user_tokens, require_auth, get_current_user_id
from db_pool import init_db_pool, get_db_connection, health_check as db_health_check
from monitoring import (
    monitor_request, metrics_endpoint, metrics_collector, 
    health_checker, start_monitoring_thread
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS properly for production
CORS(app, origins=[
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com"  # Replace with your actual frontend domain
])

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize authentication
init_auth(app)

# Initialize database pool
if not init_db_pool():
    logger.error("Failed to initialize database pool")

# Initialize user service
user_service = UserService(get_db_connection)

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", "1000"))
RATE_LIMIT_PER_DAY = int(os.environ.get("RATE_LIMIT_PER_DAY", "10000"))

# Health check endpoint (no rate limiting)
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API and database status"""
    try:
        # Check database health
        db_healthy = db_health_check()
        
        if not db_healthy:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.now().isoformat()
            }), 503
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

# Metrics endpoint (no rate limiting)
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()

# Authentication endpoints
@app.route('/auth/register', methods=['POST'])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def register():
    """Register a new user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not all([email, password, name]):
        return jsonify({"error": "Email, password, and name are required"}), 400
    
    success, result = user_service.create_user(email, password, name)
    
    if success:
        user_id = result
        access_token, refresh_token = create_user_tokens(user_id)
        
        # Record metrics
        metrics_collector.record_user_registration()
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }), 201
    else:
        return jsonify({"error": result}), 400

@app.route('/auth/login', methods=['POST'])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def login():
    """Login user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400
    
    success, result = user_service.authenticate_user(email, password)
    
    if success:
        user_data = result
        access_token, refresh_token = create_user_tokens(user_data['id'])
        
        # Record metrics
        metrics_collector.record_user_login()
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data
        }), 200
    else:
        return jsonify({"error": result}), 401

@app.route('/auth/profile', methods=['GET'])
@require_auth
@monitor_request
def get_profile():
    """Get user profile"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not found"}), 404
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user), 200

@app.route('/auth/logout', methods=['POST'])
@require_auth
@monitor_request
def logout():
    """Logout user (revoke token)"""
    from auth import revoke_token
    revoke_token()
    return jsonify({"message": "Logged out successfully"}), 200

# API Endpoint to get all products
@app.route('/products', methods=['GET'])
@app.route('/api/products', methods=['GET'])  # Keep both for compatibility
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def get_products():
    """Get all products from the database"""
    logger.info("GET /products - Fetching all products")
    
    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed for get_products")
        return jsonify({"error": "Database connection failed"}), 500

    products = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, price, image_url FROM products ORDER BY name;")
        rows = cur.fetchall()
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "imageUrl": row[4]
            })
            
            # Record product view metric
            metrics_collector.record_product_view(row[0])
            
        cur.close()
        logger.info(f"Successfully fetched {len(products)} products")
    except Error as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({"error": "Error fetching products"}), 500
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")
    
    return jsonify(products)

# API endpoint to add a product to the cart
@app.route('/cart/add', methods=['POST'])
@app.route('/api/cart/add', methods=['POST'])  # Keep both for compatibility
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def add_to_cart():
    """Add a product to the cart with validation"""
    logger.info("POST /cart/add - Adding product to cart")
    
    data = request.get_json()
    if not data:
        logger.warning("No JSON data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)

    # Input validation
    if not product_id:
        logger.warning("Product ID is required")
        return jsonify({"error": "Product ID is required"}), 400
    
    if not isinstance(quantity, int) or quantity <= 0:
        logger.warning(f"Invalid quantity: {quantity}")
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed for add_to_cart")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        
        # First, validate that the product exists
        cur.execute("SELECT id, name FROM products WHERE id = %s;", (product_id,))
        product = cur.fetchone()
        if not product:
            logger.warning(f"Product with ID {product_id} not found")
            return jsonify({"error": "Product not found"}), 404
        
        # Check if the product already exists in the cart
        cur.execute("SELECT id, quantity FROM cart_items WHERE product_id = %s;", (product_id,))
        existing_item = cur.fetchone()

        if existing_item:
            new_quantity = existing_item[1] + quantity
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s;", (new_quantity, existing_item[0]))
            message = f"Product quantity updated in cart. New quantity: {new_quantity}"
            logger.info(f"Updated cart item quantity for product {product_id}")
        else:
            cur.execute("INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s);", (product_id, quantity))
            message = f"Product '{product[1]}' added to cart"
            logger.info(f"Added new product {product_id} to cart")

        conn.commit()
        cur.close()
        
        # Record metrics
        metrics_collector.record_cart_addition(product_id)
        
        return jsonify({"message": message}), 200
    except Error as e:
        conn.rollback()
        logger.error(f"Database error adding/updating cart item: {e}")
        return jsonify({"error": "Error processing cart item"}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to get all items in the cart
@app.route('/cart', methods=['GET'])
@app.route('/api/cart', methods=['GET'])  # Keep both for compatibility
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def get_cart():
    """Get all items in the cart"""
    logger.info("GET /cart - Fetching cart items")
    
    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed for get_cart")
        return jsonify({"error": "Database connection failed"}), 500

    cart_items_data = []
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
                products p ON ci.product_id = p.id
            ORDER BY ci.created_at DESC;
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
        logger.info(f"Successfully fetched {len(cart_items_data)} cart items")
    except Error as e:
        logger.error(f"Error fetching cart items: {e}")
        return jsonify({"error": "Error fetching cart items"}), 500
    finally:
        if conn:
            conn.close()
    
    return jsonify(cart_items_data)

# API endpoint to remove an item from the cart
@app.route('/cart/remove/<int:cart_item_id>', methods=['DELETE'])
@app.route('/api/cart/remove/<int:cart_item_id>', methods=['DELETE'])  # Keep both for compatibility
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def remove_from_cart(cart_item_id):
    """Remove an item from the cart"""
    logger.info(f"DELETE /cart/remove/{cart_item_id} - Removing cart item")
    
    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed for remove_from_cart")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart_items WHERE id = %s;", (cart_item_id,))
        if cur.rowcount == 0:
            conn.rollback()
            logger.warning(f"Cart item {cart_item_id} not found")
            return jsonify({"message": "Cart item not found"}), 404
        conn.commit()
        cur.close()
        logger.info(f"Successfully removed cart item {cart_item_id}")
        return jsonify({"message": "Cart item removed successfully"}), 200
    except Error as e:
        conn.rollback()
        logger.error(f"Error removing cart item: {e}")
        return jsonify({"error": "Error removing cart item"}), 500
    finally:
        if conn:
            conn.close()

# API endpoint to update the quantity of a cart item
@app.route('/cart/update/<int:cart_item_id>', methods=['PUT'])
@app.route('/api/cart/update/<int:cart_item_id>', methods=['PUT'])  # Keep both for compatibility
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
@monitor_request
def update_cart_item(cart_item_id):
    """Update the quantity of a cart item"""
    logger.info(f"PUT /cart/update/{cart_item_id} - Updating cart item")
    
    data = request.get_json()
    if not data:
        logger.warning("No JSON data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    new_quantity = data.get('quantity')

    if not isinstance(new_quantity, int) or new_quantity <= 0:
        logger.warning(f"Invalid quantity: {new_quantity}")
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed for update_cart_item")
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s;", (new_quantity, cart_item_id))
        if cur.rowcount == 0:
            conn.rollback()
            logger.warning(f"Cart item {cart_item_id} not found")
            return jsonify({"message": "Cart item not found"}), 404
        conn.commit()
        cur.close()
        logger.info(f"Successfully updated cart item {cart_item_id} quantity to {new_quantity}")
        return jsonify({"message": "Cart item updated successfully"}), 200
    except Error as e:
        conn.rollback()
        logger.error(f"Error updating cart item: {e}")
        return jsonify({"error": "Error updating cart item"}), 500
    finally:
        if conn:
            conn.close()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f"Rate limit exceeded: {request.url}")
    
    # Record rate limit metric
    metrics_collector.record_rate_limit(request.endpoint, get_remote_address())
    
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": e.retry_after if hasattr(e, 'retry_after') else 60
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

# Run the Flask app
if __name__ == '__main__':
    # Use environment variable for debug mode, default to False for safety
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    # SSL configuration for production
    ssl_context = None
    if os.environ.get("USE_SSL", "0") == "1":
        cert_file = os.environ.get("SSL_CERT_FILE")
        key_file = os.environ.get("SSL_KEY_FILE")
        
        if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            logger.info("SSL enabled with provided certificate")
        else:
            logger.warning("SSL requested but certificate files not found or not specified")
    
    # Start monitoring thread
    start_monitoring_thread()
    
    # Add health checks
    health_checker.add_check("database", db_health_check, interval=30)
    
    # Log startup information
    logger.info(f"Starting Flask app in {'debug' if debug_mode else 'production'} mode")
    logger.info(f"Rate limiting: {RATE_LIMIT_PER_MINUTE}/min, {RATE_LIMIT_PER_HOUR}/hour, {RATE_LIMIT_PER_DAY}/day")
    logger.info(f"SSL enabled: {ssl_context is not None}")
    logger.info("Authentication, database pooling, and monitoring enabled")
    
    app.run(
        host='127.0.0.1', 
        port=5000, 
        debug=debug_mode,
        ssl_context=ssl_context
    )