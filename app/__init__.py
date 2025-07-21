import meraki
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging

db = SQLAlchemy()
migrate = Migrate()

from .meraki_api import update_splash_page_settings, add_firewall_rule, add_port_forwarding_rule, verify_port_forwarding_rule

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
            # We need a network ID to add a firewall rule. We will need to get this from the organization.
            # This is a simplification for now.
            dashboard = meraki.DashboardAPI(api_key)
            networks = dashboard.organizations.getOrganizationNetworks(org_id)
            if networks:
                network_id = networks[0]['id']
                add_firewall_rule(api_key, network_id)
                if not verify_port_forwarding_rule(api_key, network_id):
                    add_port_forwarding_rule(api_key, network_id)
            update_splash_page_settings(api_key, org_id, ssid_names)
        else:
            logging.warning("Meraki API is enabled, but one or more required environment variables are missing.")

    logging.info("Flask app created")
    return app
