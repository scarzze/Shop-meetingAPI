from flask import Blueprint, request, jsonify
from app.models import User
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data['full_name']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at
    })

@user_bp.errorhandler(404)
def user_not_found(error):
    return jsonify({"error": "User not found"}), 404