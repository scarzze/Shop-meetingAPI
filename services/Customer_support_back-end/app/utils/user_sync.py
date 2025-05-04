import os
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from app.models import db, User
import logging

logger = logging.getLogger(__name__)

def sync_user_from_auth(user_data):
    """
    Sync user data from Auth Service to the Customer Support Service database.
    This ensures that a user record exists for authenticated users.
    
    Args:
        user_data (dict): User data from Auth Service token
        
    Returns:
        User: The synchronized user record
    """
    user_id = user_data.get('id')
    if not user_id:
        logger.warning("User data missing ID, cannot sync")
        return None
    
    try:
        # Check if user already exists
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            # Create user record if it doesn't exist
            try:
                # Combine first_name and last_name for full_name field
                full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                if not full_name:
                    full_name = "Unknown User"
                
                # Use email as username if not provided
                username = user_data.get('email', f"user_{user_id}")
                email = user_data.get('email', f"user_{user_id}@example.com")
                
                # Create a secure placeholder password since we're using JWT for auth
                placeholder_password = os.urandom(16).hex()
                
                user = User(
                    id=user_id,
                    username=username,
                    email=email,
                    password=placeholder_password,  # Will never be used for auth
                    full_name=full_name
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"Created new user: {user_id} in Customer Support Service database")
                return user
            except IntegrityError:
                # In case of race condition, roll back and try to fetch again
                db.session.rollback()
                logger.warning(f"Integrity error when creating user {user_id}, rolling back")
                return User.query.filter_by(id=user_id).first()
        
        return user
        
    except (OperationalError, SQLAlchemyError) as e:
        db.session.rollback()
        logger.error(f"Database error in sync_user_from_auth: {str(e)}")
        
        # Return a mock user object when database is not available
        # This allows the service to continue functioning in production mode
        mock_user = type('obj', (object,), {
            'id': user_id,
            'username': user_data.get('email', f"user_{user_id}"),
            'email': user_data.get('email', f"user_{user_id}@example.com"),
            'full_name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or "Unknown User",
            'is_admin': user_data.get('is_admin', False),
            'is_support_agent': user_data.get('is_support_agent', False),
            'is_mock': True
        })
        
        logger.info(f"Returning mock user for {user_id} due to database unavailability")
        return mock_user
