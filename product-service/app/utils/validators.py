"""
Validation utilities for product service data inputs
"""
import re
from decimal import Decimal

def validate_category_data(data):
    """
    Validate category data
    
    Args:
        data (dict): Category data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    if not data:
        return "No data provided"
        
    if 'name' not in data or not data['name']:
        return "Category name is required"
        
    if len(data['name']) > 100:
        return "Category name must be 100 characters or less"
        
    return None

def validate_product_data(data):
    """
    Validate product data
    
    Args:
        data (dict): Product data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    if not data:
        return "No data provided"
        
    # Required fields
    if 'name' not in data or not data['name']:
        return "Product name is required"
        
    if len(data['name']) > 100:
        return "Product name must be 100 characters or less"
        
    if 'price' not in data:
        return "Product price is required"
        
    try:
        price = Decimal(str(data['price']))
        if price <= 0:
            return "Price must be a positive decimal number"
    except (ValueError, TypeError, decimal.InvalidOperation):
        return "Price must be a valid number"
        
    if 'category_id' not in data:
        return "Category ID is required"
        
    # Optional fields with validation
    if 'sku' in data and data['sku']:
        if len(data['sku']) > 50:
            return "SKU must be 50 characters or less"
            
    if 'stock_quantity' in data:
        try:
            stock = int(data['stock_quantity'])
            if stock < 0:
                return "Stock quantity cannot be negative"
        except (ValueError, TypeError):
            return "Stock quantity must be a valid integer"
            
    if 'image_url' in data and data['image_url']:
        if len(data['image_url']) > 255:
            return "Image URL must be 255 characters or less"
            
    return None

def validate_review_data(data):
    """
    Validate review data
    
    Args:
        data (dict): Review data to validate
        
    Returns:
        str: Error message if validation fails, None otherwise
    """
    if not data:
        return "No data provided"
        
    # Required fields
    if 'product_id' not in data:
        return "Product ID is required"
        
    if 'user_name' not in data or not data['user_name']:
        return "User name is required"
        
    if len(data['user_name']) > 100:
        return "User name must be 100 characters or less"
        
    if 'rating' not in data:
        return "Rating is required"
        
    try:
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return "Rating must be between 1 and 5"
    except (ValueError, TypeError):
        return "Rating must be a valid integer"
        
    return None
