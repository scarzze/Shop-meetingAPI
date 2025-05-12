from flask import Flask, jsonify
from app.models import db
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('product_service')

# Create a simple Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///product_service.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Add direct health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check received")
    return jsonify({'status': 'healthy', 'service': 'product'})

if __name__ == '__main__':
    try:
        logger.info("Starting Product Service...")
        with app.app_context():
            try:
                logger.info("Creating database tables if they don't exist...")
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as db_error:
                logger.error(f"Error creating database tables: {str(db_error)}")
                # Continue anyway - tables might already exist
        
        debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        logger.info(f"Running in {'DEBUG' if debug_mode else 'PRODUCTION'} mode")
        app.run(host='0.0.0.0', port=5006, debug=debug_mode, threaded=True)
    except Exception as e:
        logger.critical(f"Failed to start Product Service: {str(e)}")
        sys.exit(1)
