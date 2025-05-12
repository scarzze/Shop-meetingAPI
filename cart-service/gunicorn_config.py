import os
import multiprocessing

# Gunicorn configuration for production deployment

# Bind to this address and port
bind = "0.0.0.0:5001"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Threads per worker
threads = 2

# Worker class for handling requests
worker_class = "sync"

# Maximum number of simultaneous clients
worker_connections = 1000

# Timeout for worker processes
timeout = 30

# Restart workers after this many requests
max_requests = 2000
max_requests_jitter = 200

# Process name
proc_name = "cart-service"

# Access log file
accesslog = "./logs/gunicorn_access.log"

# Error log file
errorlog = "./logs/gunicorn_error.log"

# Log level
loglevel = "info"

# Process owner
# user = "www-data"
# group = "www-data"

# Preload the application for performance
preload_app = True

# Set environment variables
raw_env = [
    "FLASK_APP=app",
    "FLASK_ENV=production",
    "DEBUG_MODE=false"
]

# Allow workers to run for x seconds after receiving SIGTERM
graceful_timeout = 30
