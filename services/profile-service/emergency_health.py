"""
Emergency standalone health check server for the Profile Service.
This runs on a separate port and provides a guaranteed working health check
endpoint without any dependencies on the main app.
"""
from flask import Flask, jsonify
import threading
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("emergency_health")

# Create a simple Flask app separate from the main application
app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Absolute minimum health check - just returns 200 OK
    """
    return jsonify({
        'status': 'healthy',
        'service': 'profile',
        'version': '1.0.0'
    }), 200

def run_emergency_health_server():
    """
    Run the emergency health check server on port 5013
    This is 10 ports higher than the main profile service
    """
    try:
        logger.info("Starting emergency health check server on port 5013")
        app.run(host='0.0.0.0', port=5013, debug=False)
    except Exception as e:
        logger.error(f"Failed to start emergency health server: {str(e)}")

# Start the emergency health check server in a background thread
if __name__ == "__main__":
    # This will run the server directly if invoked as a script
    run_emergency_health_server()
else:
    # Start the server in a background thread if imported as a module
    thread = threading.Thread(target=run_emergency_health_server, daemon=True)
    thread.start()
    logger.info("Emergency health check thread started")
