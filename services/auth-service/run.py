from app import create_app
from app.models.user import db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5002, debug=debug_mode)