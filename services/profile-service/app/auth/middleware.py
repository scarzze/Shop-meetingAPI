from functools import wraps
from flask import request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv
from utils.auth_utils import auth_required, admin_required

load_dotenv()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('auth_middleware')

# This is kept for backward compatibility, but we'll now use the shared auth_utils

# Get DEBUG_MODE from environment variable
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Legacy auth_required function - replaced by shared auth_utils
# Now we use the imported auth_required from utils.auth_utils