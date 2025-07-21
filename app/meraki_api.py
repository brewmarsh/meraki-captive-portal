import meraki
import logging
import os

def get_organization_id(dashboard, org_id):
    """
    Get the organization ID. This function is simplified as the org_id is now directly provided.
    """
    return org_id

def update_splash_page_settings(api_key, org_id, ssid_names):
    """
    Update the splash page settings for the given SSIDs.
    """
    logging.info("Initializing Meraki dashboard API")
    dashboard = meraki.DashboardAPI(api_key)

    if not org_id:
        logging.error("Meraki Organization ID is not provided.")
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
