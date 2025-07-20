from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

from .meraki_api import update_splash_page_settings

def create_app():
    """Create and configure an instance of the Flask application."""
    logging.info("Creating Flask app")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    logging.info("Initializing database")
    db.init_app(app)
    migrate.init_app(app, db)

    from . import routes
    logging.info("Registering blueprint")
    app.register_blueprint(routes.bp)

    if os.environ.get('MERAKI_API_ENABLED') == 'true':
        logging.info("Meraki API is enabled, updating splash page settings")
        api_key = os.environ.get('MERAKI_API_KEY')
        org_name = os.environ.get('MERAKI_ORG_NAME')
        ssid_names = os.environ.get('MERAKI_SSID_NAMES', '').split(',')
        if api_key and org_name and ssid_names:
            update_splash_page_settings(api_key, org_name, ssid_names)
        else:
            logging.warning("Meraki API is enabled, but one or more required environment variables are missing.")

    logging.info("Flask app created")
    return app
