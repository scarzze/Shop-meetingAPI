import os
from sqlalchemy.exc import IntegrityError
from ..models import db, Profile

def sync_profile_from_auth(user_data):
    """
    Sync user profile data from Auth Service to the Profile Service database.
    This ensures that a profile record exists for authenticated users.
    
    Args:
        user_data (dict): User data from Auth Service token
        
    Returns:
        Profile: The synchronized profile record
    """
    user_id = user_data.get('id')
    if not user_id:
        return None
        
    # Convert user_id to string since the Profile model expects it as a string
    user_id = str(user_id)
        
    # Check if profile already exists
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        # Create profile record if it doesn't exist
        try:
            # Combine first_name and last_name since Profile model has a single 'name' field
            name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            if not name:
                name = "Unknown User"
                
            profile = Profile(
                user_id=user_id,
                name=name,
                email=user_data.get('email', 'unknown@example.com'),
                phone='',
                preferences={},
                notification_settings={}
            )
            db.session.add(profile)
            db.session.commit()
            return profile
        except IntegrityError:
            # In case of race condition, roll back and try to fetch again
            db.session.rollback()
            return Profile.query.filter_by(user_id=user_id).first()
    
    return profile
