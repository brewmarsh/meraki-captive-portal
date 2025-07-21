import meraki
import os
import logging

def get_dashboard():
    """
    Initializes and returns a Meraki Dashboard API instance.
    """
    api_key = os.environ.get('MERAKI_API_KEY')
    if not api_key:
        logging.warning("MERAKI_API_KEY not found in environment variables.")
        return None

    # Suppress informational logging from the Meraki library
    logging.getLogger('meraki').setLevel(logging.WARNING)

    dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
    return dashboard
