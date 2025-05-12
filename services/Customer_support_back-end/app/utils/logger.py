import logging
import os
from datetime import datetime

def setup_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    logger = logging.getLogger('customer_support')
    logger.setLevel(logging.INFO)

    # Create file handler for authentication logs
    auth_handler = logging.FileHandler('logs/auth.log')
    auth_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    auth_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(auth_handler)

    return logger

logger = setup_logger()

def log_auth_success(user_id, endpoint):
    """Log successful authentication"""
    logger.info(f"Successful authentication - User ID: {user_id} - Endpoint: {endpoint}")

def log_auth_failure(error, ip_address, endpoint):
    """Log failed authentication attempts"""
    logger.warning(
        f"Authentication failure - IP: {ip_address} - "
        f"Endpoint: {endpoint} - Error: {error}"
    )

def log_support_agent_action(agent_id, action, ticket_id):
    """Log support agent actions"""
    logger.info(
        f"Support Agent Action - Agent ID: {agent_id} - "
        f"Action: {action} - Ticket ID: {ticket_id}"
    )
