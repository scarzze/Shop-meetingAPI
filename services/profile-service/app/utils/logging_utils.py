import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name='profile-service', log_level=None):
    """
    Set up and configure the logger for the Profile Service
    
    Args:
        name (str): Name of the logger
        log_level (str): Log level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Determine log level from environment or parameter
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create log directory if it doesn't exist
    log_dir = os.environ.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{name}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log the log level
    logger.info(f"Logging initialized with level: {log_level}")
    
    return logger
