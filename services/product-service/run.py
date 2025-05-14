from flask import Flask, jsonify, request, make_response
from app.models import db
from app.routes.product_routes import bp as product_bp
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
# Use absolute path for SQLite database to avoid path confusion
absolute_db_path = os.path.abspath('services/product-service/instance/product_service.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{absolute_db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Log the database URI for diagnostic purposes
logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Add direct health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check received")
    response = jsonify({'status': 'healthy', 'service': 'product'})
    return response
    
# Add a direct OPTIONS handler for the root route
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    # Always add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# Register blueprints after CORS setup
db.init_app(app)
app.register_blueprint(product_bp)

# Special handler for preflight requests to blueprint routes
@app.route('/api/v1/products', methods=['OPTIONS'])
@app.route('/api/v1/products/<path:path>', methods=['OPTIONS'])
def products_options_handler(path=None):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

if __name__ == '__main__':
    try:
        logger.info("Starting Product Service...")
        with app.app_context():
            try:
                logger.info("Creating database tables if they don't exist...")
                db.create_all()
                logger.info("Database tables created successfully")
                
                # Log database connection and product count for diagnostic purposes
                from app.models import Product
                product_count = Product.query.count()
                logger.info(f"Found {product_count} products in the database")
                if product_count > 0:
                    sample = Product.query.first()
                    logger.info(f"Sample product: {sample.name if sample else 'None'}")
            except Exception as db_error:
                logger.error(f"Error creating database tables: {str(db_error)}")
                # Continue anyway - tables might already exist
        
        # Force DEBUG_MODE to False to ensure we're using actual database data
        debug_mode = False  # Hardcoded to ensure we're using the actual database
        logger.info(f"Running in {'DEBUG' if debug_mode else 'PRODUCTION'} mode")
        app.run(host='0.0.0.0', port=5006, debug=debug_mode, threaded=True)
    except Exception as e:
        logger.critical(f"Failed to start Product Service: {str(e)}")
        sys.exit(1)
