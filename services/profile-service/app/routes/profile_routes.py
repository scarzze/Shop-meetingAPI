from flask import Blueprint, jsonify, request
from app.models import Profile, db
from app.auth.middleware import auth_required
from app.utils.validators import ProfileSchema, validate_request_data

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/<user_id>', methods=["GET"])
@auth_required
def get_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to create profile'}), 500
    
    return jsonify({
        'id': profile.id,
        'user_id': profile.user_id,
        'name': profile.name,
        'email': profile.email,
        'phone': profile.phone,
        'preferences': profile.preferences,
        'notification_settings': profile.notification_settings,
        'created_at': profile.created_at.isoformat(),
        'updated_at': profile.updated_at.isoformat()
    })

@bp.route('', methods=['PATCH'])
@auth_required
def update_profile():
    current_user_id = request.user_id
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        profile = Profile(user_id=current_user_id)
        db.session.add(profile)
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No update data provided'}), 400
    
    # Validate request data using ProfileSchema
    validated_data, errors = validate_request_data(ProfileSchema, data, partial=True)
    if errors:
        return jsonify({'message': 'Validation error', 'errors': errors}), 422
    
    try:
        # Update only validated fields
        for field, value in validated_data.items():
            setattr(profile, field, value)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile', 'error': str(e)}), 500
    
    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'name': profile.name,
            'email': profile.email,
            'phone': profile.phone,
            'preferences': profile.preferences,
            'updated_at': profile.updated_at.isoformat()
        }
    })