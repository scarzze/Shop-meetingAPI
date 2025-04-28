from flask import Blueprint, jsonify, request
from app.models import Profile, db

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/<user_id>', methods=['GET'])
def get_profile(user_id):
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

@bp.route('/', methods=['PATCH'])
def update_profile():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'message': 'user_id is required in JSON body'}), 400

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    if 'name' in data:
        profile.name = data['name']
    if 'avatar' in data:
        profile.avatar = data['avatar']
    if 'preferences' in data:
        profile.preferences = data['preferences']
    db.session.commit()

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




