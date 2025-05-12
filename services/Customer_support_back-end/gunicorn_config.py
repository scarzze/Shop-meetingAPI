import os
import multiprocessing

# Server Socket
bind = "0.0.0.0:5004"

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"  # Use gevent for WebSocket support
worker_connections = 1000

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Process Naming
proc_name = "customer_support_service"

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Timeout settings
timeout = 120  # Seconds
graceful_timeout = 60  # Seconds
keep_alive = 5  # Seconds

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Debugging
reload = os.environ.get("DEBUG_MODE", "false").lower() == "true"
preload_app = True

# For use with socketio, we need to handle it specifically
wsgi_app = "wsgi:application"

# When SCRIPT_NAME is set, gunicorn's forwarded_allow_ips needs to be '*'
forwarded_allow_ips = '*'
