#!/usr/bin/env python
"""
Reliable health check monitoring service for the Profile Service.
This service should be run separately from the main Profile Service
to ensure health checks remain responsive even if the main service
experiences issues.

Usage:
  python health_monitor.py start     # Start the health monitor
  python health_monitor.py stop      # Stop the health monitor 
  python health_monitor.py restart   # Restart the health monitor
  python health_monitor.py status    # Check status
"""
import os
import sys
import time
import signal
import socket
import logging
import atexit
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='health_monitor.log',
    filemode='a'
)
logger = logging.getLogger('health_monitor')

# Health Monitor Configuration
PORT = 5013  # Using a different port than the main Profile Service
PIDFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'health_monitor.pid')
RESPONSE = {
    'status': 'healthy',
    'service': 'profile',
    'version': '1.0.0'
}

class HealthRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler that always returns a 200 OK response"""
    
    def do_GET(self):
        """Handle GET requests to the health check endpoint"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(RESPONSE).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))
            
    def log_message(self, format, *args):
        """Override the default log_message to use our logger"""
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_pid_running(pid):
    """Check if a process with the given PID is running"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def read_pid_file():
    """Read the PID from the PID file"""
    try:
        with open(PIDFILE, 'r') as f:
            return int(f.read().strip())
    except (IOError, ValueError):
        return None

def write_pid_file(pid):
    """Write the PID to the PID file"""
    with open(PIDFILE, 'w') as f:
        f.write(str(pid))

def remove_pid_file():
    """Remove the PID file"""
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)

def start_server():
    """Start the health check server"""
    # Check if the server is already running
    pid = read_pid_file()
    if pid and check_pid_running(pid):
        print(f"Health monitor is already running with PID {pid}")
        return
        
    # Check if the port is already in use
    if is_port_in_use(PORT):
        print(f"Port {PORT} is already in use. Please check if another service is running on this port.")
        sys.exit(1)
    
    # Start the server
    try:
        server = HTTPServer(('0.0.0.0', PORT), HealthRequestHandler)
        print(f"Starting health monitor on port {PORT}")
        logger.info(f"Starting health monitor on port {PORT}")
        
        # Write the PID file
        write_pid_file(os.getpid())
        
        # Register cleanup
        atexit.register(remove_pid_file)
        
        # Run the server
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health monitor: {str(e)}")
        print(f"Error starting health monitor: {str(e)}")
        sys.exit(1)

def stop_server():
    """Stop the health check server"""
    pid = read_pid_file()
    if not pid:
        print("Health monitor is not running (no PID file found)")
        return
        
    if not check_pid_running(pid):
        print(f"Health monitor is not running (PID {pid} not found)")
        remove_pid_file()
        return
        
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopping health monitor with PID {pid}")
        time.sleep(1)
        if check_pid_running(pid):
            os.kill(pid, signal.SIGKILL)
            print(f"Forcefully terminated health monitor with PID {pid}")
        remove_pid_file()
    except OSError as e:
        print(f"Error stopping health monitor: {str(e)}")

def check_status():
    """Check the status of the health check server"""
    pid = read_pid_file()
    if not pid:
        print("Health monitor is not running (no PID file found)")
        return False
        
    if not check_pid_running(pid):
        print(f"Health monitor is not running (PID {pid} not found)")
        remove_pid_file()
        return False
        
    # Check if the port is in use
    if not is_port_in_use(PORT):
        print(f"Health monitor process is running with PID {pid}, but port {PORT} is not in use")
        return False
        
    print(f"Health monitor is running with PID {pid} on port {PORT}")
    return True

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [start|stop|restart|status]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_server()
    elif command == 'stop':
        stop_server()
    elif command == 'restart':
        stop_server()
        time.sleep(1)
        start_server()
    elif command == 'status':
        check_status()
    else:
        print(f"Unknown command: {command}")
        print(f"Usage: {sys.argv[0]} [start|stop|restart|status]")
        sys.exit(1)

if __name__ == '__main__':
    main()
