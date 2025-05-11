from app import create_app, socketio

application = create_app()

if __name__ == "__main__":
    socketio.run(application, host='0.0.0.0', port=5004)
