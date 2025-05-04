from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=5005)
