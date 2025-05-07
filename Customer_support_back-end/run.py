import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
<<<<<<< HEAD
    socketio.run(app, debug=True, host='0.0.0.0', port=5004)
=======
    debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5004))
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
>>>>>>> acc80f31cc71d75c021e7e5d3d9d04c002037e37
