import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(app_name, log_level=None):
    """
    Set up a production-ready logger that:
    1. Logs to a file with proper rotation
    2. Uses structured JSON format for machine parsing
    3. Includes timestamp, service name, log level, and message
    4. Respects production vs development environment
    
    Args:
        app_name (str): The name of the application (service)
        log_level (str, optional): The log level to use. Defaults to None.
    
    Returns:
        logger: Configured logger object
    """
    # Determine log level based on environment
    if log_level is None:
        debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        log_level = 'DEBUG' if debug_mode else 'INFO'
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'{app_name}.log')
    
    # Create a custom logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()
    
    # Create handlers
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10485760,  # 10MB
        backupCount=5,      # Keep 5 backup files
        encoding='utf-8'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set log level for handlers
    file_handler.setLevel(getattr(logging, log_level))
    console_handler.setLevel(getattr(logging, log_level))
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Export a singleton logger instance for the service
cart_logger = setup_logger('cart-service')

def log_to_central_service(log_entry, service_name, log_level='INFO'):
    """
    Function to send logs to a hypothetical central logging service.
    This can be implemented when a central logging system is set up.
    
    Args:
        log_entry (str): The log message
        service_name (str): The name of the service generating the log
        log_level (str): The log level
    """
    # This would normally send the log to a central logging service
    # For now, just log it locally
    logger = logging.getLogger(service_name)
    logger.log(getattr(logging, log_level), f"[CENTRAL] {log_entry}")
