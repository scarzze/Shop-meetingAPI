import os
import logging
import sys
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask application
app = create_app()

# NOTE: Don't add any routes here - they're already defined in app/__init__.py

if __name__ == '__main__':
    try:
        debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
        port = int(os.environ.get('PORT', 5004))
        logger.info(f"Starting Customer Support Service on port {port} with debug_mode={debug_mode}")
        
        # Use standard Flask run for simplicity
        app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start Customer Support Service: {str(e)}")
        raise
