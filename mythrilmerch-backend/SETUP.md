# Backend Setup Guide

## Environment Configuration

Create a `.env` file in the `mythrilmerch-backend` directory with the following content:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=your_strong_password_here

# Flask Configuration
FLASK_DEBUG=0
FLASK_ENV=production

# CORS Configuration (comma-separated list of allowed origins)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://your-frontend-domain.com

# Rate Limiting Configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# SSL Configuration (for production)
USE_SSL=1
SSL_CERT_FILE=/etc/ssl/certs/mythrilmerch.crt
SSL_KEY_FILE=/etc/ssl/private/mythrilmerch.key
```

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Run the database migration
psql -h localhost -U ecommerce_user -d ecommerce_db -f ../db/migrations/001_initial_schema.sql
```

4. Start the Flask server:
```bash
python app.py
```

## Production Deployment

### 1. SSL Certificate Setup

Run the SSL setup script as root:

```bash
sudo ./setup_ssl.sh your-domain.com admin@your-domain.com
```

This script will:
- Generate self-signed certificates (for testing)
- Set up Let's Encrypt certificates (recommended for production)
- Use existing certificates
- Create necessary directories and users

### 2. Systemd Service Setup

1. Copy the service file to systemd:
```bash
sudo cp mythrilmerch-api.service /etc/systemd/system/
```

2. Update the environment variables in the service file:
```bash
sudo nano /etc/systemd/system/mythrilmerch-api.service
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mythrilmerch-api
sudo systemctl start mythrilmerch-api
```

### 3. Gunicorn Configuration

The application includes a production-ready Gunicorn configuration:

```bash
# Start with Gunicorn (development)
gunicorn --config gunicorn.conf.py app:app

# Start with Gunicorn (production)
gunicorn --config gunicorn.conf.py --bind 0.0.0.0:443 app:app
```

## Bug Fixes Implemented

### 1. **API Route Mismatch (Critical)**
- ✅ Added routes without `/api/` prefix to match frontend calls
- ✅ Kept `/api/` routes for backward compatibility
- ✅ Fixed: Frontend was calling `/products` but backend only had `/api/products`

### 2. **Input Validation**
- ✅ Added validation for product existence before adding to cart
- ✅ Added JSON data validation for all POST/PUT requests
- ✅ Added quantity validation (must be positive integer)

### 3. **Error Handling**
- ✅ Added comprehensive error handlers (404, 500, general exceptions)
- ✅ Improved database connection error handling
- ✅ Added proper logging throughout the application

### 4. **Security Improvements**
- ✅ Configured CORS properly with specific allowed origins
- ✅ Added connection timeout for database connections
- ✅ Removed hardcoded credentials from code
- ✅ **NEW: Rate limiting implemented**
- ✅ **NEW: SSL/HTTPS support**

### 5. **Rate Limiting**
- ✅ **NEW: Flask-Limiter integration**
- ✅ **NEW: Configurable rate limits per minute/hour/day**
- ✅ **NEW: Rate limit error handling (429 responses)**
- ✅ **NEW: Health check endpoint excluded from rate limiting**

### 6. **SSL/HTTPS Support**
- ✅ **NEW: SSL certificate configuration**
- ✅ **NEW: Gunicorn SSL support**
- ✅ **NEW: Automatic certificate renewal (Let's Encrypt)**
- ✅ **NEW: Production-ready systemd service**

### 7. **Logging & Monitoring**
- ✅ Added structured logging for all operations
- ✅ Added health check endpoint (`/health`)
- ✅ Added request logging and error tracking

### 8. **Database Operations**
- ✅ Added product validation before cart operations
- ✅ Improved SQL queries with proper ordering
- ✅ Added better transaction handling

### 9. **API Improvements**
- ✅ Added health check endpoint
- ✅ Better error messages and status codes
- ✅ Consistent response format

## API Endpoints

### Health Check
- `GET /health` - Check API and database status (no rate limiting)

### Products
- `GET /products` - Get all products (rate limited)
- `GET /api/products` - Get all products (legacy, rate limited)

### Cart
- `GET /cart` - Get cart items (rate limited)
- `POST /cart/add` - Add item to cart (rate limited)
- `DELETE /cart/remove/<id>` - Remove item from cart (rate limited)
- `PUT /cart/update/<id>` - Update cart item quantity (rate limited)

## Rate Limiting

The API implements rate limiting with the following defaults:
- **60 requests per minute** per IP address
- **1000 requests per hour** per IP address
- **10000 requests per day** per IP address

Rate limits can be configured via environment variables:
- `RATE_LIMIT_PER_MINUTE`
- `RATE_LIMIT_PER_HOUR`
- `RATE_LIMIT_PER_DAY`

When rate limits are exceeded, the API returns a 429 status code with a helpful error message.

## SSL Configuration

### Development
For development, SSL is disabled by default. To enable:
```bash
export USE_SSL=1
export SSL_CERT_FILE=/path/to/cert.pem
export SSL_KEY_FILE=/path/to/key.pem
```

### Production
For production deployment:
1. Run the SSL setup script: `sudo ./setup_ssl.sh your-domain.com`
2. Use Gunicorn with SSL: `gunicorn --config gunicorn.conf.py app:app`
3. Or use the systemd service which includes SSL configuration

## Testing the API

1. Test health check:
```bash
curl http://localhost:5000/health
```

2. Test products endpoint:
```bash
curl http://localhost:5000/products
```

3. Test adding to cart:
```bash
curl -X POST http://localhost:5000/cart/add \
  -H "Content-Type: application/json" \
  -d '{"productId": 1, "quantity": 1}'
```

4. Test rate limiting:
```bash
# Make multiple rapid requests to see rate limiting in action
for i in {1..70}; do curl http://localhost:5000/products; done
```

## Production Deployment Notes

1. **Environment Variables**: Always use environment variables for sensitive data
2. **CORS**: Update `ALLOWED_ORIGINS` with your actual frontend domain
3. **Database**: Use a production database with proper security
4. **Logging**: Configure proper log rotation and monitoring
5. **SSL**: Use HTTPS in production (now supported)
6. **Rate Limiting**: Configure appropriate rate limits for your use case
7. **Monitoring**: Set up monitoring for rate limit violations and API performance

## Security Considerations

- ✅ Input validation implemented
- ✅ SQL injection protection (parameterized queries)
- ✅ CORS properly configured
- ✅ Error messages don't expose sensitive information
- ✅ **NEW: Rate limiting prevents abuse**
- ✅ **NEW: SSL/HTTPS encryption**
- ✅ **NEW: Systemd security hardening**
- ⚠️ Consider adding authentication for production
- ⚠️ Consider adding request size limits
- ⚠️ Consider implementing API key authentication for external clients

## Monitoring and Logs

### View Service Status
```bash
sudo systemctl status mythrilmerch-api
```

### View Application Logs
```bash
sudo journalctl -u mythrilmerch-api -f
```

### View Access Logs
```bash
sudo tail -f /var/log/mythrilmerch/access.log
```

### View Error Logs
```bash
sudo tail -f /var/log/mythrilmerch/error.log
```

### Monitor Rate Limiting
```bash
# Check for rate limit violations
sudo journalctl -u mythrilmerch-api | grep "Rate limit exceeded"
``` 