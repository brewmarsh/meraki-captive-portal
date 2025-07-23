import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
cache = Cache()
mail = Mail()

def create_app(config_name='default'):
    """Create and configure an instance of the Flask application."""
    logging.info(f"Creating Flask app with config '{config_name}'")
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.Config')

    logging.info("Initializing database")
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    login.login_view = 'routes.login'

    from . import routes
    logging.info("Registering blueprint")
    app.register_blueprint(routes.bp)

    from app.models import User

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from . import meraki_api
    meraki_api_enabled = os.environ.get('MERAKI_API_ENABLED', 'false').lower() == 'true'
    logging.info(f"Meraki API Enabled: {meraki_api_enabled}")

    if meraki_api_enabled:
        api_key = os.environ.get('MERAKI_API_KEY')
        org_id = os.environ.get('MERAKI_ORG_ID')
        ssid_names_str = os.environ.get('MERAKI_SSID_NAMES', '')
        ssid_names = ssid_names_str.split(',')

        logging.info(f"MERAKI_API_KEY: {'set' if api_key else 'not set'}")
        logging.info(f"MERAKI_ORG_ID: {org_id}")
        logging.info(f"MERAKI_SSID_NAMES: {ssid_names_str}")

        if api_key and org_id and ssid_names:
            logging.info("All Meraki environment variables are set, proceeding with splash page update.")
            dashboard = get_dashboard()
            if dashboard:
                networks = dashboard.organizations.getOrganizationNetworks(org_id)
                if networks:
                    network_id = networks[0]['id']
                    if not meraki_api.verify_port_forwarding_rule(dashboard, network_id):
                        meraki_api.add_port_forwarding_rule(dashboard, network_id)
                meraki_api.update_splash_page_settings(dashboard, org_id, ssid_names)
        else:
            logging.warning("Meraki API is enabled, but one or more required environment variables are missing.")

    from . import errors
    app.register_blueprint(errors.bp)

    logging.info("Flask app created")
    return app
