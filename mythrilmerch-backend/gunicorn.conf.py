# Gunicorn configuration file for production deployment
import os
import multiprocessing

# Server socket
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:5000")
backlog = 2048

# Worker processes
workers = os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# SSL Configuration
keyfile = os.environ.get("SSL_KEY_FILE")
certfile = os.environ.get("SSL_CERT_FILE")
if keyfile and certfile and os.path.exists(keyfile) and os.path.exists(certfile):
    bind = f"{bind}:443"
    ssl_version = "TLSv1_2"

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "mythrilmerch-api"

# Server mechanics
daemon = False
pidfile = os.environ.get("GUNICORN_PID_FILE", "/tmp/gunicorn.pid")
user = os.environ.get("GUNICORN_USER")
group = os.environ.get("GUNICORN_GROUP")
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker has been initialized."""
    worker.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called just before a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker has been aborted."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid) 