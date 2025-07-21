import meraki
import logging
import os

def get_organization_id(dashboard, org_id):
    """
    Get the organization ID. This function is simplified as the org_id is now directly provided.
    """
    return org_id

def get_external_url(api_key, org_id, network_id):
    """
    Get the external URL of the appliance.
    """
    logging.info("Initializing Meraki dashboard API to get external URL")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        status = dashboard.appliance.getOrganizationApplianceVpnStats(org_id)
        #This is a simplification, a more robust solution would be to iterate through the networks and find the one with the correct network_id
        return status[0]['wanIp']
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting external URL: {e}")
        return None

def add_firewall_rule(api_key, network_id):
    """
    Add a firewall rule to the appliance to allow traffic to the captive portal.
    """
    logging.info("Initializing Meraki dashboard API to add firewall rule")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(network_id)
        new_rule = {
            'comment': 'Allow traffic to captive portal',
            'policy': 'allow',
            'protocol': 'tcp',
            'destPort': os.environ.get('PORT', 5001),
            'destCidr': 'any'
        }
        rules['rules'].insert(0, new_rule)
        dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(network_id, rules=rules['rules'])
        logging.info("Firewall rule added successfully")
    except meraki.APIError as e:
        logging.error(f"Meraki API error adding firewall rule: {e}")

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
