from app import create_app
from app.models import db
import os

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Only attempt database operations if not in debug mode
    if not debug_mode:
        with app.app_context():
            db.create_all()
    else:
        print("Running in DEBUG_MODE - skipping database operations")
        
    app.run(port=5003, debug=debug_mode)