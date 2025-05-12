import os
from sqlalchemy.exc import IntegrityError, OperationalError
from models import db, User

def sync_user_from_auth(user_data):
    """
    Sync user data from Auth Service to the Order Service database.
    This ensures that a user record exists for authenticated users.
    
    Args:
        user_data (dict): User data from Auth Service token
        
    Returns:
        User: The synchronized user record or None if database not available
    """
    user_id = user_data.get('id')
    if not user_id:
        return None
        
    try:
        # Check if user already exists
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            # Create user record if it doesn't exist
            try:
                user = User(
                    id=user_id,
                    email=user_data.get('email', 'unknown@example.com'),
                    first_name=user_data.get('first_name', 'Unknown'),
                    last_name=user_data.get('last_name', 'User')
                )
                db.session.add(user)
                db.session.commit()
                return user
            except IntegrityError:
                # In case of race condition, roll back and try to fetch again
                db.session.rollback()
                return User.query.filter_by(id=user_id).first()
        
        return user
    except OperationalError:
        # If database is not available, just return None
        # The application will fall back to using mock data
        print(f"Unable to connect to database. User {user_id} will not be synced.")
        return None
