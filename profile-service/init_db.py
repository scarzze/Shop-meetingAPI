from run import app
from app import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting database initialization...")

with app.app_context():
    # Drop all tables first to ensure a clean slate
    logger.debug("Dropping existing tables...")
    db.drop_all()
    
    logger.debug("Creating database tables...")
    db.create_all()
    logger.debug("Database tables created successfully!")