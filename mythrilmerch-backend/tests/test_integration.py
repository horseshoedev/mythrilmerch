"""
Integration tests for MythrilMerch API
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app
from auth import UserService
from db_pool import get_db_connection

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """Mock database connection"""
    with patch('app.get_db_connection') as mock:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock.return_value = mock_conn
        yield mock_conn, mock_cur

@pytest.fixture
def auth_headers():
    """Get authentication headers"""
    def _auth_headers(token):
        return {'Authorization': f'Bearer {token}'}
    return _auth_headers

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client, mock_db):
        """Test successful health check"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = (1,)
        
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
    
    def test_health_check_db_failure(self, client, mock_db):
        """Test health check with database failure"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.side_effect = Exception("Database error")
        
        response = client.get('/health')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'
        assert data['database'] == 'error'

class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_register_success(self, client, mock_db):
        """Test successful user registration"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = None  # No existing user
        mock_cur.fetchone.side_effect = [None, (1,)]  # No existing user, then user_id
        
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPass123',
            'name': 'Test User'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/auth/register', json={
            'email': 'invalid-email',
            'password': 'TestPass123',
            'name': 'Test User'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid email format' in data['error']
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'weak',
            'name': 'Test User'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Password must be at least 8 characters long' in data['error']
    
    def test_login_success(self, client, mock_db):
        """Test successful login"""
        mock_conn, mock_cur = mock_db
        
        # Mock user data with hashed password
        from auth import hash_password
        hashed_password = hash_password('TestPass123')
        mock_cur.fetchone.return_value = (1, hashed_password, 'Test User')
        
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, mock_db):
        """Test login with invalid credentials"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = None
        
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid email or password' in data['error']

class TestProductEndpoints:
    """Test product endpoints"""
    
    def test_get_products_success(self, client, mock_db):
        """Test successful product retrieval"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchall.return_value = [
            (1, 'Test Product', 'Test Description', 29.99, 'test.jpg'),
            (2, 'Another Product', 'Another Description', 49.99, 'another.jpg')
        ]
        
        response = client.get('/products')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['name'] == 'Test Product'
        assert data[0]['price'] == 29.99
    
    def test_get_products_db_error(self, client, mock_db):
        """Test product retrieval with database error"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchall.side_effect = Exception("Database error")
        
        response = client.get('/products')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'Error fetching products' in data['error']

class TestCartEndpoints:
    """Test cart endpoints"""
    
    def test_add_to_cart_success(self, client, mock_db):
        """Test successful cart addition"""
        mock_conn, mock_cur = mock_db
        
        # Mock product exists and no existing cart item
        mock_cur.fetchone.side_effect = [
            (1, 'Test Product'),  # Product exists
            None  # No existing cart item
        ]
        
        response = client.post('/cart/add', json={
            'productId': 1,
            'quantity': 2
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Product' in data['message']
        assert 'added to cart' in data['message']
    
    def test_add_to_cart_product_not_found(self, client, mock_db):
        """Test cart addition with non-existent product"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = None  # Product not found
        
        response = client.post('/cart/add', json={
            'productId': 999,
            'quantity': 1
        })
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Product not found' in data['error']
    
    def test_get_cart_success(self, client, mock_db):
        """Test successful cart retrieval"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchall.return_value = [
            (1, 1, 2, 'Test Product', 'Description', 29.99, 'test.jpg')
        ]
        
        response = client.get('/cart')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Test Product'
        assert data[0]['quantity'] == 2

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_enforced(self, client, mock_db):
        """Test that rate limiting is enforced"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchall.return_value = []  # Empty products list
        
        # Make multiple requests to trigger rate limiting
        responses = []
        for i in range(65):  # Exceed the 60/minute limit
            response = client.get('/products')
            responses.append(response.status_code)
        
        # Check that some requests were rate limited
        assert 429 in responses, "Rate limiting should be triggered"
    
    def test_health_endpoint_not_rate_limited(self, client, mock_db):
        """Test that health endpoint is not rate limited"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = (1,)
        
        # Make multiple requests to health endpoint
        responses = []
        for i in range(10):
            response = client.get('/health')
            responses.append(response.status_code)
        
        # All should succeed (no rate limiting)
        assert all(status == 200 for status in responses)

class TestProtectedEndpoints:
    """Test protected endpoints with authentication"""
    
    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoint without authentication"""
        response = client.get('/auth/profile')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Authentication required' in data['message']
    
    @patch('auth.get_jwt_identity')
    def test_protected_endpoint_with_token(self, mock_identity, client, mock_db):
        """Test protected endpoint with valid token"""
        mock_identity.return_value = 1
        
        mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = (1, 'test@example.com', 'Test User', '2023-01-01')
        
        # Create a mock token (in real test, you'd get this from login)
        headers = {'Authorization': 'Bearer mock-token'}
        response = client.get('/auth/profile', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'test@example.com'
        assert data['name'] == 'Test User'

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Endpoint not found' in data['error']
    
    def test_500_error(self, client, mock_db):
        """Test 500 error handling"""
        mock_conn, mock_cur = mock_db
        mock_cur.fetchall.side_effect = Exception("Database error")
        
        response = client.get('/products')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'Error fetching products' in data['error'] 