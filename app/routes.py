from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from .models import Client
from . import db
import logging
from datetime import datetime

bp = Blueprint('routes', __name__)

logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

@bp.route('/')
def splash():
    """
    The splash page for the captive portal.
    It captures client data and redirects to the success page.
    """
    try:
        # Meraki provides client MAC, IP, and other details in the query string
        client_mac = request.args.get('client_mac')
        client_ip = request.args.get('client_ip')
        user_agent = request.headers.get('User-Agent')

        if client_mac and client_ip:
            # Check if the client is already in the database
            client = Client.query.filter_by(mac_address=client_mac).first()
            if client:
                client.last_seen = datetime.utcnow()
            else:
                client = Client(mac_address=client_mac, ip_address=client_ip, user_agent=user_agent)
                db.session.add(client)

            db.session.commit()

            # Store redirect URL from Meraki in session
            session['redirect_url'] = request.args.get('base_grant_url')

            return render_template('splash.html')
        else:
            # If Meraki data is not present, it might be a direct access attempt.
            return "Direct access is not supported."

    except Exception as e:
        current_app.logger.error(f"Error in splash page: {e}")
        return "An error occurred. Please try again later.", 500

@bp.route('/connect')
def connect():
    """
    This route is hit after the user clicks "connect" or the timer runs out.
    It redirects the user to their original destination.
    """
    redirect_url = session.get('redirect_url', 'http://www.google.com')
    return redirect(redirect_url)
