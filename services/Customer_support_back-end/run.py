from flask import Flask, jsonify
import os
import logging

# Create a minimal Flask application with just essential functionality
app = Flask(__name__)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('customer-support')

# Simple health check endpoint that will always work
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'customer-support',
        'version': '1.0.0'
    })

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'customer-support',
        'message': 'Customer Support Service is running'
    })

if __name__ == '__main__':
    # Get port from environment with fallback to 5004
    port = int(os.environ.get('PORT', 5004))
    debug = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    
    logger.info(f"Starting minimal Customer Support Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

