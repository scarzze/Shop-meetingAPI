from app import create_app, socketio

app = create_app()

# Update Socket.IO configuration
socketio.init_app(app,
    cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"],  # Add Vite's default port
    async_mode='threading',
    ping_timeout=60
)

if __name__ == '__main__':
    socketio.run(app, 
        debug=True, 
        host='0.0.0.0', 
        port=5004
    )
