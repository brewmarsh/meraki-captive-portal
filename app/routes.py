from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from .models import Client
from . import db
import logging
from datetime import datetime
from .meraki_api import get_external_url, verify_port_forwarding_rule, verify_splash_page
from .meraki_dashboard import get_dashboard

bp = Blueprint('routes', __name__)

@bp.route('/')
def splash():
    """
    The splash page for the captive portal.
    It captures client data and redirects to the success page.
    """
    logging.info("Splash page requested")
    try:
        # Meraki provides client MAC, IP, and other details in the query string
        client_mac = request.args.get('client_mac')
        client_ip = request.args.get('client_ip')
        user_agent = request.headers.get('User-Agent')

        if 'X-Forwarded-For' in request.headers:
            external_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
            logging.info(f"External IP: {external_ip}")

        logging.debug(f"Request arguments: client_mac={client_mac}, client_ip={client_ip}")
        logging.debug(f"User-Agent: {user_agent}")

        if client_mac and client_ip:
            logging.info(f"Processing client with MAC: {client_mac} and IP: {client_ip}")
            # Check if the client is already in the database
            client = Client.query.filter_by(mac_address=client_mac).first()
            if client:
                logging.info("Client found in database, updating last_seen")
                client.last_seen = datetime.utcnow()
            else:
                logging.info("Client not found, creating new entry")
                client = Client(mac_address=client_mac, ip_address=client_ip, user_agent=user_agent)
                db.session.add(client)

            db.session.commit()
            logging.info("Client data saved to database")

            # Store redirect URL from Meraki in session
            redirect_url = request.args.get('base_grant_url')
            session['redirect_url'] = redirect_url
            logging.info(f"Stored redirect URL in session: {redirect_url}")

            return render_template('splash.html')
        else:
            # If Meraki data is not present, it might be a direct access attempt.
            logging.warning("Direct access to splash page without Meraki data")
            return "Direct access is not supported."

    except Exception as e:
        logging.error(f"Error in splash page: {e}", exc_info=True)
        return "An error occurred. Please try again later.", 500

@bp.route('/connect')
def connect():
    """
    This route is hit after the user clicks "connect" or the timer runs out.
    It redirects the user to their original destination.
    """
    redirect_url = session.get('redirect_url', 'http://www.google.com')
    logging.info(f"Redirecting user to {redirect_url}")
    return redirect(redirect_url)

import ipaddress
import os

from flask import send_from_directory

@bp.before_request
def restrict_admin_access():
    if request.path == '/admin':
        logging.info("Admin page access attempt")
        allowed_subnet = os.environ.get('ADMIN_SUBNET')
        if allowed_subnet:
            try:
                # Get the real IP address from the X-Forwarded-For header if present
                if 'X-Forwarded-For' in request.headers:
                    remote_addr = ipaddress.ip_address(request.headers.getlist("X-Forwarded-For")[0].split(',')[0])
                else:
                    remote_addr = ipaddress.ip_address(request.remote_addr)

                logging.debug(f"Remote address: {remote_addr}")
                logging.debug(f"Allowed subnet: {allowed_subnet}")

                allowed_network = ipaddress.ip_network(allowed_subnet, strict=False)
                if remote_addr not in allowed_network:
                    logging.warning(f"Admin access denied for {remote_addr}")
                    return send_from_directory(os.path.join(current_app.root_path, 'static', 'images'), 'access_denied.png')
                logging.info(f"Admin access granted for {remote_addr}")
            except ValueError:
                # Log this error, as it's a configuration issue
                logging.error(f"Invalid ADMIN_SUBNET: {allowed_subnet}", exc_info=True)
                return "Internal server error.", 500

@bp.route('/admin')
def admin():
    """
    The admin page, which displays some basic stats from the database.
    """
    logging.info("Admin page loaded")
    try:
        total_clients = Client.query.count()
        clients = Client.query.order_by(Client.last_seen.desc()).limit(10).all()
        logging.debug(f"Total clients: {total_clients}, showing last 10")

        meraki_org_id = os.environ.get('MERAKI_ORG_ID')
        meraki_ssid_names = os.environ.get('MERAKI_SSID_NAMES')
        external_url = None
        port_forwarding_rule_active = False
        splash_page_set_correctly = False
        dashboard = get_dashboard()
        if dashboard and meraki_org_id:
            networks = dashboard.organizations.getOrganizationNetworks(meraki_org_id)
            if networks:
                network_id = networks[0]['id']
                external_url = get_external_url(dashboard, meraki_org_id, network_id)
                port_forwarding_rule_active = verify_port_forwarding_rule(dashboard, network_id)
                if meraki_ssid_names:
                    # For simplicity, we only check the first SSID
                    splash_page_set_correctly = verify_splash_page(dashboard, network_id, meraki_ssid_names.split(',')[0])

        auto_refresh_seconds = os.environ.get('AUTO_REFRESH_SECONDS', 120)

        return render_template('admin.html',
                                 total_clients=total_clients,
                                 clients=clients,
                                 meraki_org_id=meraki_org_id,
                                 meraki_ssid_names=meraki_ssid_names,
                                 external_url=external_url,
                                 auto_refresh_seconds=auto_refresh_seconds,
                                 port_forwarding_rule_active=port_forwarding_rule_active,
                                 splash_page_set_correctly=splash_page_set_correctly)
    except Exception as e:
        logging.error(f"Error loading admin page: {e}", exc_info=True)
        return "An error occurred while loading the admin page.", 500

@bp.route('/set_refresh', methods=['POST'])
def set_refresh():
    """
    Set the refresh interval in the session.
    """
    refresh_interval = request.form.get('refresh_interval')
    if refresh_interval:
        session['auto_refresh_seconds'] = refresh_interval
    return redirect(url_for('routes.admin'))

@bp.route('/force_refresh', methods=['POST'])
def force_refresh():
    """
    Force a refresh of the admin page.
    """
    return redirect(url_for('routes.admin'))
