"""
Monitoring and metrics for MythrilMerch API
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, generate_latest,
    CONTENT_TYPE_LATEST, CollectorRegistry
)
import time
import logging
from functools import wraps
from flask import request, Response
import threading

logger = logging.getLogger(__name__)

# Create a custom registry for our metrics
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# Business metrics
PRODUCT_VIEWS = Counter(
    'product_views_total',
    'Total product views',
    ['product_id'],
    registry=registry
)

CART_ADDITIONS = Counter(
    'cart_additions_total',
    'Total items added to cart',
    ['product_id'],
    registry=registry
)

USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations',
    registry=registry
)

USER_LOGINS = Counter(
    'user_logins_total',
    'Total user logins',
    registry=registry
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    'database_active_connections',
    'Number of active database connections',
    registry=registry
)

ERROR_RATE = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint'],
    registry=registry
)

RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total',
    'Total rate limit violations',
    ['endpoint', 'ip_address'],
    registry=registry
)

# Performance metrics
DB_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    registry=registry
)

CACHE_HIT_RATIO = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio (0-1)',
    registry=registry
)

# Alert thresholds
ALERT_THRESHOLDS = {
    'error_rate_threshold': 0.05,  # 5% error rate
    'response_time_threshold': 2.0,  # 2 seconds
    'database_connection_threshold': 0.8,  # 80% of max connections
    'rate_limit_threshold': 10  # 10 rate limit hits per minute
}

class MetricsCollector:
    """Collector for custom metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_times = []
        self.error_counts = {}
        self.rate_limit_counts = {}
    
    def record_request(self, method, endpoint, status_code, duration, request_size, response_size):
        """Record request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(request_size)
        RESPONSE_SIZE.labels(method=method, endpoint=endpoint).observe(response_size)
        
        # Store for alerting
        self.request_times.append(duration)
        if len(self.request_times) > 1000:  # Keep last 1000 requests
            self.request_times.pop(0)
    
    def record_error(self, error_type, endpoint):
        """Record error metrics"""
        ERROR_RATE.labels(error_type=error_type, endpoint=endpoint).inc()
        
        key = f"{error_type}:{endpoint}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def record_rate_limit(self, endpoint, ip_address):
        """Record rate limit violations"""
        RATE_LIMIT_HITS.labels(endpoint=endpoint, ip_address=ip_address).inc()
        
        key = f"{endpoint}:{ip_address}"
        self.rate_limit_counts[key] = self.rate_limit_counts.get(key, 0) + 1
    
    def record_product_view(self, product_id):
        """Record product view"""
        PRODUCT_VIEWS.labels(product_id=str(product_id)).inc()
    
    def record_cart_addition(self, product_id):
        """Record cart addition"""
        CART_ADDITIONS.labels(product_id=str(product_id)).inc()
    
    def record_user_registration(self):
        """Record user registration"""
        USER_REGISTRATIONS.inc()
    
    def record_user_login(self):
        """Record user login"""
        USER_LOGINS.inc()
    
    def update_database_metrics(self, active_connections, max_connections):
        """Update database connection metrics"""
        ACTIVE_CONNECTIONS.set(active_connections)
        
        # Calculate connection ratio
        if max_connections > 0:
            connection_ratio = active_connections / max_connections
            if connection_ratio > ALERT_THRESHOLDS['database_connection_threshold']:
                logger.warning(f"High database connection usage: {connection_ratio:.2%}")
    
    def update_cache_metrics(self, hit_ratio):
        """Update cache metrics"""
        CACHE_HIT_RATIO.set(hit_ratio)
    
    def check_alerts(self):
        """Check for alert conditions"""
        alerts = []
        
        # Check error rate
        total_requests = sum(REQUEST_COUNT._metrics.values())
        total_errors = sum(ERROR_RATE._metrics.values())
        
        if total_requests > 0:
            error_rate = total_errors / total_requests
            if error_rate > ALERT_THRESHOLDS['error_rate_threshold']:
                alerts.append(f"High error rate: {error_rate:.2%}")
        
        # Check response time
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            if avg_response_time > ALERT_THRESHOLDS['response_time_threshold']:
                alerts.append(f"High response time: {avg_response_time:.2f}s")
        
        # Check rate limit violations
        recent_rate_limits = sum(self.rate_limit_counts.values())
        if recent_rate_limits > ALERT_THRESHOLDS['rate_limit_threshold']:
            alerts.append(f"High rate limit violations: {recent_rate_limits}")
        
        return alerts

# Global metrics collector
metrics_collector = MetricsCollector()

def monitor_request(f):
    """Decorator to monitor request metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        start_size = len(request.get_data()) if request.get_data() else 0
        
        try:
            response = f(*args, **kwargs)
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            response_size = len(response.get_data()) if hasattr(response, 'get_data') else 0
            
            # Record metrics
            duration = time.time() - start_time
            metrics_collector.record_request(
                method=request.method,
                endpoint=request.endpoint,
                status_code=status_code,
                duration=duration,
                request_size=start_size,
                response_size=response_size
            )
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            metrics_collector.record_error(
                error_type=type(e).__name__,
                endpoint=request.endpoint
            )
            
            # Re-raise the exception
            raise
    
    return decorated_function

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest(registry)

def metrics_endpoint():
    """Metrics endpoint for Prometheus"""
    return Response(get_metrics(), mimetype=CONTENT_TYPE_LATEST)

class HealthChecker:
    """Health check and monitoring"""
    
    def __init__(self):
        self.checks = {}
        self.last_check = {}
    
    def add_check(self, name, check_func, interval=60):
        """Add a health check"""
        self.checks[name] = {
            'func': check_func,
            'interval': interval,
            'last_result': None
        }
    
    def run_checks(self):
        """Run all health checks"""
        results = {}
        current_time = time.time()
        
        for name, check_info in self.checks.items():
            last_check_time = self.last_check.get(name, 0)
            
            if current_time - last_check_time >= check_info['interval']:
                try:
                    result = check_info['func']()
                    check_info['last_result'] = result
                    self.last_check[name] = current_time
                    results[name] = result
                except Exception as e:
                    logger.error(f"Health check {name} failed: {e}")
                    results[name] = False
            else:
                results[name] = check_info['last_result']
        
        return results

# Global health checker
health_checker = HealthChecker()

def start_monitoring_thread():
    """Start background monitoring thread"""
    def monitor_loop():
        while True:
            try:
                # Check alerts
                alerts = metrics_collector.check_alerts()
                if alerts:
                    logger.warning(f"Alerts detected: {alerts}")
                
                # Run health checks
                health_results = health_checker.run_checks()
                for check_name, result in health_results.items():
                    if not result:
                        logger.error(f"Health check failed: {check_name}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)
    
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info("Monitoring thread started") 