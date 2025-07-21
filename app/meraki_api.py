import meraki
import logging
import os

def get_organization_id(dashboard, org_id):
    """
    Get the organization ID. This function is simplified as the org_id is now directly provided.
    """
    return org_id

def get_appliance_serial(dashboard, network_id):
    """
    Get the serial number of the appliance in a network.
    """
    try:
        devices = dashboard.networks.getNetworkDevices(network_id)
        for device in devices:
            if 'MX' in device['model']:
                return device['serial']
        return None
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting appliance serial: {e}")
        return None

def get_external_url(api_key, org_id, network_id):
    """
    Get the external URL of the appliance.
    """
    logging.info("Initializing Meraki dashboard API to get external URL")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        serial = get_appliance_serial(dashboard, network_id)
        if serial:
            interface = dashboard.devices.getDeviceManagementInterface(serial)
            return interface.get('ddnsHostnames', {}).get('activeDdnsHostname', 'Not available')
        return "Appliance not found"
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting external URL: {e}")
        return None

def verify_port_forwarding_rule(api_key, network_id):
    """
    Verify that the port forwarding rule is active.
    """
    logging.info("Initializing Meraki dashboard API to verify port forwarding rule")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallPortForwardingRules(network_id)
        for rule in rules['rules']:
            if rule['name'] == 'Captive Portal':
                return True
        return False
    except meraki.APIError as e:
        logging.error(f"Meraki API error verifying port forwarding rule: {e}")
        return False

def verify_splash_page(api_key, network_id, ssid_name):
    """
    Verify that the splash page is set correctly for a given SSID.
    """
    logging.info(f"Initializing Meraki dashboard API to verify splash page for SSID '{ssid_name}'")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        ssids = dashboard.wireless.getNetworkWirelessSsids(network_id)
        for ssid in ssids:
            if ssid['name'] == ssid_name:
                splash_settings = dashboard.wireless.getNetworkWirelessSsidSplashSettings(network_id, ssid['number'])
                external_url = get_external_url(api_key, os.environ.get('MERAKI_ORG_ID'), network_id)
                external_port = os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001))
                expected_splash_url = f"http://{external_url}:{external_port}/"
                return splash_settings.get('splashUrl') == expected_splash_url
        return False
    except meraki.APIError as e:
        logging.error(f"Meraki API error verifying splash page: {e}")
        return False

def add_port_forwarding_rule(api_key, network_id):
    """
    Add a port forwarding rule to the appliance to forward traffic to the captive portal.
    """
    logging.info("Initializing Meraki dashboard API to add port forwarding rule")
    dashboard = meraki.DashboardAPI(api_key)
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallPortForwardingRules(network_id)
        new_rule = {
            'name': 'Captive Portal',
            'lanIp': os.environ.get('LAN_IP'),
            'publicPort': os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001)),
            'localPort': os.environ.get('PORT', 5001),
            'protocol': 'tcp',
            'allowedIps': ['any']
        }
        rules['rules'].insert(0, new_rule)
        dashboard.appliance.updateNetworkApplianceFirewallPortForwardingRules(network_id, rules=rules['rules'])
        logging.info("Port forwarding rule added successfully")
    except meraki.APIError as e:
        logging.error(f"Meraki API error adding port forwarding rule: {e}")

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
            'destPort': os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001)),
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
                    external_url = get_external_url(api_key, org_id, network['id'])
                    external_port = os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001))
                    splash_page_settings = {
                        'splashPage': 'custom',
                        'splashUrl': f"http://{external_url}:{external_port}/"
                    }
                    dashboard.wireless.updateNetworkWirelessSsidSplashSettings(
                        networkId=network['id'],
                        number=ssid['number'],
                        **splash_page_settings
                    )
    except meraki.APIError as e:
        logging.error(f"Meraki API error updating splash page settings: {e}")
