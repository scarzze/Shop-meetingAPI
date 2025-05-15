from flask_sqlalchemy import SQLAlchemy
from flask import request, url_for
from typing import Dict, Any, List

class PaginationHelper:
    @staticmethod
    def paginate_query(query, model, page: int = 1, per_page: int = 10):
        """
        Paginates a SQLAlchemy query and returns paginated results with metadata
        """
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        next_url = url_for(
            request.endpoint,
            page=page + 1,
            per_page=per_page,
            **request.args
        ) if pagination.has_next else None
        
        prev_url = url_for(
            request.endpoint,
            page=page - 1,
            per_page=per_page,
            **request.args
        ) if pagination.has_prev else None

        return {
            'items': pagination.items,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_url': next_url,
                'prev_url': prev_url
            }
        }

    @staticmethod
    def get_pagination_params() -> tuple:
        """
        Gets pagination parameters from request args
        """
        try:
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 10)), 100)
            return page, per_page
        except (TypeError, ValueError):
            return 1, 10