from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
from .models import Client, User, Profile
from . import db
from .forms import LoginForm, RegistrationForm, ProfileForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
import logging
from datetime import datetime
from .meraki_api import get_external_url, verify_port_forwarding_rule, verify_splash_page
from .meraki_dashboard import get_dashboard
from .email import send_email

bp = Blueprint('routes', __name__)

@bp.route('/')
@login_required
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

            timer_duration = current_app.config.get('SPLASH_TIMER_SECONDS', 10)
            return render_template('splash.html', timer_duration=timer_duration)
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
    redirect_url = session.get('redirect_url', 'https://www.reddit.com')
    logging.info(f"Redirecting user to {redirect_url}")
    return redirect(redirect_url)

import ipaddress
import os

from flask import send_from_directory

@bp.before_request
def restrict_admin_access():
    if request.path == '/admin':
        logging.info("Admin page access attempt")
        allowed_subnet = current_app.config.get('ADMIN_SUBNET') or os.environ.get('ADMIN_SUBNET')
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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('routes.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('routes.admin'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.admin'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.email.data)
        user.set_password(form.password.data)
        profile = Profile()
        user.profile = profile
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

from sqlalchemy import func

@bp.route('/chart-data')
@login_required
def chart_data():
    # Connections per day
    connections_per_day = db.session.query(func.date(Client.first_seen), func.count(Client.id)).group_by(func.date(Client.first_seen)).all()
    labels = [row[0].strftime('%Y-%m-%d') for row in connections_per_day]
    data = [row[1] for row in connections_per_day]

    # Top user agents
    top_user_agents = db.session.query(Client.user_agent, func.count(Client.id)).group_by(Client.user_agent).order_by(func.count(Client.id).desc()).limit(5).all()
    user_agent_labels = [row[0] for row in top_user_agents]
    user_agent_data = [row[1] for row in top_user_agents]

    return {
        'connections_per_day': {
            'labels': labels,
            'data': data
        },
        'top_user_agents': {
            'labels': user_agent_labels,
            'data': user_agent_data
        }
    }

@bp.route('/meraki_status')
def meraki_status():
    """
    The Meraki status page, which displays detailed information about the Meraki integration.
    """
    logging.info("Meraki status page loaded")
    try:
        meraki_org_id = os.environ.get('MERAKI_ORG_ID')
        meraki_ssid_names = os.environ.get('MERAKI_SSID_NAMES')
        meraki_api_key_set = bool(os.environ.get('MERAKI_API_KEY'))
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

        return render_template('meraki_status.html',
                                 meraki_api_key_set=meraki_api_key_set,
                                 meraki_org_id=meraki_org_id,
                                 meraki_ssid_names=meraki_ssid_names,
                                 external_url=external_url,
                                 port_forwarding_rule_active=port_forwarding_rule_active,
                                 splash_page_set_correctly=splash_page_set_correctly)
    except Exception as e:
        logging.error(f"Error loading Meraki status page: {e}", exc_info=True)
        return "An error occurred while loading the Meraki status page.", 500

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.profile.dark_mode = form.dark_mode.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('routes.profile'))
    elif request.method == 'GET':
        form.dark_mode.data = current_user.profile.dark_mode
    return render_template('profile.html', title='Profile', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('routes.admin'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            send_email(user.username,
                       'Reset Your Password',
                       render_template('email/reset_password.html',
                                       user=user, token=token))
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('routes.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('routes.admin'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('routes.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('routes.login'))
    return render_template('reset_password.html', form=form)
