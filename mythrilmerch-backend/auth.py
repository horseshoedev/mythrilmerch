"""
Authentication module for MythrilMerch API
"""

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    verify_jwt_in_request
)
from flask_bcrypt import Bcrypt
from functools import wraps
import re
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Initialize bcrypt
bcrypt = Bcrypt()

# JWT token blocklist (in production, use Redis)
token_blocklist = set()

def init_auth(app):
    """Initialize authentication with Flask app"""
    from flask_jwt_extended import JWTManager
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = app.config.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    jwt = JWTManager(app)
    
    # Initialize bcrypt with app
    bcrypt.init_app(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Request does not contain an access token',
            'error': 'authorization_required'
        }), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in token_blocklist

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has been revoked',
            'error': 'token_revoked'
        }), 401

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.check_password_hash(hashed_password, password)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            return jsonify({'message': 'Authentication required'}), 401
    return decorated_function

def get_current_user_id():
    """Get current user ID from JWT token"""
    try:
        return get_jwt_identity()
    except Exception:
        return None

def create_user_tokens(user_id):
    """Create access and refresh tokens for a user"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return access_token, refresh_token

def revoke_token():
    """Revoke the current token"""
    jti = get_jwt()["jti"]
    token_blocklist.add(jti)
    logger.info(f"Token revoked: {jti}")

class UserService:
    """Service class for user operations"""
    
    def __init__(self, db_connection_func):
        self.get_db_connection = db_connection_func
    
    def create_user(self, email, password, name):
        """Create a new user"""
        # Validate input
        if not validate_email(email):
            return False, "Invalid email format"
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return False, message
        
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        conn = self.get_db_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cur = conn.cursor()
            
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return False, "User with this email already exists"
            
            # Hash password and create user
            hashed_password = hash_password(password)
            cur.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (email, name.strip(), hashed_password)
            )
            user_id = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            
            logger.info(f"User created: {email}")
            return True, user_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating user: {e}")
            return False, "Error creating user"
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate a user"""
        conn = self.get_db_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, password_hash, name FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()
            
            if not user:
                return False, "Invalid email or password"
            
            user_id, password_hash, name = user
            
            if not verify_password(password, password_hash):
                return False, "Invalid email or password"
            
            logger.info(f"User authenticated: {email}")
            return True, {"id": user_id, "email": email, "name": name}
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, "Authentication error"
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, email, name, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            user = cur.fetchone()
            cur.close()
            
            if user:
                return {
                    "id": user[0],
                    "email": user[1],
                    "name": user[2],
                    "created_at": user[3].isoformat() if user[3] else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            conn.close()
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        allowed_fields = {'name', 'email'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False, "No valid fields to update"
        
        conn = self.get_db_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cur = conn.cursor()
            
            # Build update query
            set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
            values = list(update_fields.values()) + [user_id]
            
            cur.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
            
            if cur.rowcount == 0:
                return False, "User not found"
            
            conn.commit()
            cur.close()
            
            logger.info(f"User updated: {user_id}")
            return True, "User updated successfully"
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating user: {e}")
            return False, "Error updating user"
        finally:
            conn.close() 