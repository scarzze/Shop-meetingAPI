from flask import Blueprint, jsonify, request
from app.models import Address, Profile, db
from app.auth.middleware import auth_required
import logging
import os
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('address', __name__, url_prefix='/addresses')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
@auth_required
def get_addresses():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock address data
    if debug_mode:
        mock_addresses = [
            {
                'id': 1,
                'address_type': 'home',
                'is_default': True,
                'name': 'Home Address',
                'street': '123 Main Street',
                'city': 'Example City',
                'state': 'Example State',
                'country': 'Example Country',
                'postal_code': '12345',
                'phone': '+1234567890'
            },
            {
                'id': 2,
                'address_type': 'work',
                'is_default': False,
                'name': 'Work Address',
                'street': '456 Office Boulevard',
                'city': 'Business City',
                'state': 'Business State',
                'country': 'Example Country',
                'postal_code': '67890',
                'phone': '+0987654321'
            }
        ]
        logger.info("Returning mock addresses in DEBUG_MODE")
        return jsonify(mock_addresses), 200
    
    # Not in DEBUG_MODE - use database
    try:
        current_user_id = request.user_id
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404

        addresses = Address.query.filter_by(profile_id=profile.id).all()
        return jsonify([{
            'id': addr.id,
            'address_type': addr.address_type,
            'is_default': addr.is_default,
            'name': addr.name,
            'street': addr.street,
            'city': addr.city,
            'state': addr.state,
            'country': addr.country,
            'postal_code': addr.postal_code,
            'phone': addr.phone
        } for addr in addresses])
    except Exception as e:
        logger.error(f"Error retrieving addresses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('', methods=['POST'])
@auth_required
def add_address():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock response for adding an address
    if debug_mode:
        data = request.get_json()
        required_fields = ['name', 'street', 'city', 'country', 'postal_code']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Create a mock response with the new address
        mock_address = {
            'id': 3,  # Simulate a new ID
            'address_type': data.get('address_type', 'shipping'),
            'is_default': data.get('is_default', False),
            'name': data.get('name'),
            'street': data.get('street'),
            'city': data.get('city'),
            'state': data.get('state', ''),
            'country': data.get('country'),
            'postal_code': data.get('postal_code'),
            'phone': data.get('phone', '')
        }
        logger.info("Created mock address in DEBUG_MODE")
        return jsonify(mock_address), 201
        
    # Not in DEBUG_MODE - use database
    try:
        current_user_id = request.user_id
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404

        data = request.get_json()
        required_fields = ['name', 'street', 'city', 'country', 'postal_code']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            if data.get('is_default', False):
                # Remove default flag from other addresses of same type
                Address.query.filter_by(
                    profile_id=profile.id,
                    address_type=data.get('address_type', 'shipping'),
                    is_default=True
                ).update({'is_default': False})

            address = Address(
                profile_id=profile.id,
                address_type=data.get('address_type', 'shipping'),
                is_default=data.get('is_default', False),
                name=data['name'],
                street=data['street'],
                city=data['city'],
                state=data.get('state'),
                country=data['country'],
                postal_code=data['postal_code'],
                phone=data.get('phone')
            )

            db.session.add(address)
            db.session.commit()

            return jsonify({
                'message': 'Address added successfully',
                'address_id': address.id
            }), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while adding address: {str(e)}")
            return jsonify({'error': 'Failed to add address'}), 500

    except Exception as e:
        logger.error(f"Unexpected error while adding address: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:address_id>', methods=['PUT'])
@auth_required
def update_address(address_id):
    try:
        current_user_id = request.user_id
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404

        address = Address.query.filter_by(id=address_id, profile_id=profile.id).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404

        data = request.get_json()
        try:
            if data.get('is_default', False) and not address.is_default:
                # Remove default flag from other addresses of same type
                Address.query.filter_by(
                    profile_id=profile.id,
                    address_type=address.address_type,
                    is_default=True
                ).update({'is_default': False})
                address.is_default = True

            for field in ['name', 'street', 'city', 'state', 'country', 'postal_code', 'phone']:
                if field in data:
                    setattr(address, field, data[field])

            db.session.commit()
            return jsonify({'message': 'Address updated successfully'})

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while updating address: {str(e)}")
            return jsonify({'error': 'Failed to update address'}), 500

    except Exception as e:
        logger.error(f"Unexpected error while updating address: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:address_id>', methods=['DELETE'])
@auth_required
def delete_address(address_id):
    try:
        current_user_id = request.user_id
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404

        address = Address.query.filter_by(id=address_id, profile_id=profile.id).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404

        try:
            was_default = address.is_default
            address_type = address.address_type
            
            db.session.delete(address)
            
            if was_default:
                # Make another address of same type default if available
                new_default = Address.query.filter_by(
                    profile_id=profile.id,
                    address_type=address_type
                ).first()
                if new_default:
                    new_default.is_default = True
                    
            db.session.commit()
            return jsonify({'message': 'Address deleted successfully'})

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while deleting address: {str(e)}")
            return jsonify({'error': 'Failed to delete address'}), 500

    except Exception as e:
        logger.error(f"Unexpected error while deleting address: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500