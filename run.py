from app import create_app
import os
import logging

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting application")

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 5001))
        debug = log_level == 'DEBUG'
        logging.info(f"Application running on port {port} with debug mode {'on' if debug else 'off'}")
        app.run(port=port, debug=debug)
    except Exception as e:
        logging.critical(f"Application failed to start: {e}", exc_info=True)
        exit(1)
