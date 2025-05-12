from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, date
import re

# Enhanced validation patterns
PHONE_REGEX = r'^\+?1?\d{9,15}$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class PreferencesSchema(Schema):
    favorite_categories = fields.List(fields.String(), required=False)
    preferred_price_range = fields.Dict(
        keys=fields.String(validate=validate.OneOf(['min', 'max'])),
        values=fields.Float(validate=validate.Range(min=0)),
        required=False
    )
    notification_frequency = fields.String(
        validate=validate.OneOf(['daily', 'weekly', 'monthly']),
        required=False,
        default='weekly'
    )

class NotificationSettingsSchema(Schema):
    email_marketing = fields.Boolean(required=False, default=True)
    order_updates = fields.Boolean(required=False, default=True)
    price_alerts = fields.Boolean(required=False, default=True)
    new_products = fields.Boolean(required=False, default=False)
    recommendations = fields.Boolean(required=False, default=True)
    alert_threshold = fields.Float(required=False, default=0.1)  # 10% price drop

class ProfileSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, validate=validate.Regexp(EMAIL_REGEX))
    phone = fields.String(validate=validate.Regexp(PHONE_REGEX), required=False)
    date_of_birth = fields.Date(required=False)
    preferences = fields.Nested(PreferencesSchema, required=False)
    notification_settings = fields.Nested(NotificationSettingsSchema, required=False)

    @validates('date_of_birth')
    def validate_birth_date(self, value):
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 13:
                raise ValidationError('User must be at least 13 years old')
            if age > 120:
                raise ValidationError('Invalid birth date')

class AddressSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    address_type = fields.String(required=True, validate=validate.OneOf(['shipping', 'billing']))
    street = fields.String(required=True, validate=validate.Length(min=5, max=255))
    city = fields.String(required=True, validate=validate.Length(min=2, max=100))
    state = fields.String(required=False, validate=validate.Length(max=100))
    country = fields.String(required=True, validate=validate.Length(min=2, max=100))
    postal_code = fields.String(required=True, validate=validate.Length(min=3, max=20))
    phone = fields.String(validate=validate.Regexp(PHONE_REGEX), required=False)
    is_default = fields.Boolean(required=False, default=False)

class PriceAlertSchema(Schema):
    product_id = fields.String(required=True)
    target_price = fields.Float(required=True, validate=validate.Range(min=0.01))
    notify_on_price_drop = fields.Boolean(required=False, default=True)
    notification_threshold = fields.Float(required=False, default=0.05)  # 5% threshold

class WishlistItemSchema(Schema):
    product_id = fields.String(required=True)
    notify_on_price_drop = fields.Boolean(required=False, default=False)
    target_price = fields.Float(required=False, validate=validate.Range(min=0.01))
    priority = fields.Integer(required=False, validate=validate.Range(min=1, max=5))

def validate_request_data(schema_class, data, partial=False):
    """
    Validate request data against a schema
    
    Args:
        schema_class: The schema class to use for validation
        data: The data to validate
        partial: Whether to allow partial updates
    
    Returns:
        tuple: (validated_data, errors)
    """
    schema = schema_class()
    try:
        validated_data = schema.load(data, partial=partial)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages

def validate_profile_data(data, partial=False):
    """
    Validate profile data using ProfileSchema
    
    Args:
        data: The profile data to validate
        partial: Whether to allow partial updates
    
    Returns:
        tuple: (validated_data, errors)
    """
    return validate_request_data(ProfileSchema, data, partial)