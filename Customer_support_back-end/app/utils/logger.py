import logging

# Create a logger for the application
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)

# Create a stream handler to output logs to the console
handler = logging.StreamHandler()

# Define the log format: Timestamp, Log Level, and the Message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# You can use this logger in your routes or anywhere in your app
 