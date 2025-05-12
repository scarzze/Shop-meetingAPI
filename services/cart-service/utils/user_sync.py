import os
from sqlalchemy.exc import IntegrityError
from models import db, User

def sync_user_from_auth(user_data):
    """
    Sync user data from Auth Service to the Cart Service database.
    This ensures that a user record exists for authenticated users.
    
    Args:
        user_data (dict): User data from Auth Service token
        
    Returns:
        User: The synchronized user record
    """
    user_id = user_data.get('id')
    if not user_id:
        return None
        
    # Check if user already exists
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        # Create user record if it doesn't exist
        try:
            # The User model in Cart Service only has id and username fields
            username = f"{user_data.get('first_name', 'Unknown')} {user_data.get('last_name', 'User')}"
            user = User(
                id=user_id,
                username=username
            )
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            # In case of race condition, roll back and try to fetch again
            db.session.rollback()
            return User.query.filter_by(id=user_id).first()
    
    return user
