import meraki
import logging
import os

def get_network_id(dashboard, org_name):
    """
    Get the network ID for a given organization name.
    """
    try:
        organizations = dashboard.organizations.getOrganizations()
        for org in organizations:
            if org['name'] == org_name:
                return org['id']
        return None
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting organization ID: {e}")
        return None

def update_splash_page_settings(api_key, org_name, ssid_names):
    """
    Update the splash page settings for the given SSIDs.
    """
    logging.info("Initializing Meraki dashboard API")
    dashboard = meraki.DashboardAPI(api_key)

    org_id = get_network_id(dashboard, org_name)
    if not org_id:
        logging.error(f"Could not find organization ID for '{org_name}'")
        return

    try:
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        for network in networks:
            ssids = dashboard.wireless.getNetworkWirelessSsids(network['id'])
            for ssid in ssids:
                if ssid['name'] in ssid_names:
                    logging.info(f"Updating splash page for SSID '{ssid['name']}' in network '{network['name']}'")
                    splash_page_settings = {
                        'splashPage': 'custom',
                        'splashUrl': f"http://{os.environ.get('PUBLIC_IP', 'localhost')}:{os.environ.get('PORT', 5001)}/"
                    }
                    dashboard.wireless.updateNetworkWirelessSsidSplashSettings(
                        networkId=network['id'],
                        number=ssid['number'],
                        **splash_page_settings
                    )
    except meraki.APIError as e:
        logging.error(f"Meraki API error updating splash page settings: {e}")
