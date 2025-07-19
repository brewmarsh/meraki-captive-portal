from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

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

    logging.info("Flask app created")
    return app
