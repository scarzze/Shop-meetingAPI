class PaginationHelper:
    @staticmethod
    def get_pagination_params():
        """
        Get pagination parameters from the request object
        
        Returns:
            tuple: (page, per_page) - pagination parameters from request
        """
        from flask import request
        
        # Get page and per_page from query parameters
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            # Ensure page is at least 1
            page = max(1, page)
            
            # Ensure per_page is between 1 and 100
            per_page = max(1, min(100, per_page))
            
            return page, per_page
        except (ValueError, TypeError):
            # Default values if conversion fails
            return 1, 10
    
    @staticmethod
    def paginate_query(query, model_class, page, per_page):
        """
        Paginate SQLAlchemy query and return standardized response format
        
        Args:
            query: SQLAlchemy query object
            model_class: SQLAlchemy model class with to_dict method
            page: Current page number (1-indexed)
            per_page: Number of items per page
            
        Returns:
            dict: Dictionary with paginated results and metadata
        """
        # Ensure page is at least 1
        page = max(1, page)
        
        # Get total count of items
        total_items = query.count()
        
        # Calculate pagination values
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 1
        
        # Apply pagination to query
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        
        # Convert items to dictionaries
        items_dict = [item.to_dict() if hasattr(item, 'to_dict') else item for item in items]
        
        # Build response with items and pagination metadata
        result = {
            'items': items_dict,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        return result
        
    @staticmethod
    def paginate_results(query, page, per_page):
        """
        Paginate SQLAlchemy query results
        
        Args:
            query: SQLAlchemy query object
            page: Current page number (1-indexed)
            per_page: Number of items per page
            
        Returns:
            dict: Dictionary with paginated results and metadata
        """
        # Ensure page is at least 1
        page = max(1, page)
        
        # Get total count of items
        total = query.count()
        
        # Calculate pagination values
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        has_prev = page > 1
        has_next = page < total_pages
        
        # Apply pagination to query
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        
        # Build pagination metadata
        pagination = {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': has_prev, 
            'has_next': has_next,
            'items': items
        }
        
        return pagination
