from flask import Blueprint, jsonify, request
from app.models import Profile, db
from app.auth.middleware import auth_required

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/me', methods=['GET'])
@auth_required
def get_profile():
    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return jsonify({
        'id': profile.id,
        'user_id': profile.user_id,
        'name': profile.name,
        'avatar': profile.avatar,
        'preferences': profile.preferences,
        'created_at': profile.created_at.isoformat(),
        'updated_at': profile.updated_at.isoformat()
    })

@bp.route('/me', methods=['PATCH'])
@auth_required
def update_profile():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'message': 'Invalid JSON in request body'}), 400

    user_id = request.user_id
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    if 'name' in data:
        profile.name = data['name']
    if 'avatar' in data:
        profile.avatar = data['avatar']
    if 'preferences' in data:
        profile.preferences = data['preferences']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating profile'}), 500

    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'name': profile.name,
            'avatar': profile.avatar,
            'preferences': profile.preferences,
            'updated_at': profile.updated_at.isoformat()
        }
    })




