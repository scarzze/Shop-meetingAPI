"""
Auth utilities for the Profile Service
This file reexports the auth utilities from the root utils directory
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path to make root-level imports work
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Import from the root utils directory
from utils.auth_utils import auth_required, admin_required, support_agent_required, auth_utils

# Re-export the functions and objects
__all__ = ['auth_required', 'admin_required', 'support_agent_required', 'auth_utils']
