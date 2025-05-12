import os
import multiprocessing

# Bind to 0.0.0.0:5006
bind = "0.0.0.0:5006"

# Worker configuration
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
threads = int(os.environ.get('GUNICORN_THREADS', '2'))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
raw_env = []
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Server hooks
def on_starting(server):
    """Log that Gunicorn is starting."""
    print("Starting product-service Gunicorn server with {} workers".format(workers))

def on_exit(server):
    """Log that Gunicorn is shutting down."""
    print("Shutting down Gunicorn")
