from app import create_app
from app.models import db
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the emergency health check server
# This starts a separate mini-server on port 5013 that provides a guaranteed working health check
import emergency_health
logger.info("Emergency health check server imported")

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Always attempt to create tables, but handle any errors gracefully
    try:
        with app.app_context():
            logger.info("Initializing database tables...")
            db.create_all()
            logger.info("Database initialization complete")
    except Exception as e:
        # Log the error but continue starting the application
        logger.error(f"Database initialization error: {str(e)}")
        logger.info("Continuing to start application despite database error")
    
    # Set host to 0.0.0.0 to make it accessible externally
    logger.info(f"Starting Profile Service on port 5003 (debug_mode={debug_mode})")
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)