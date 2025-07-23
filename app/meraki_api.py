import logging
import os
import meraki
from .meraki_dashboard import get_dashboard
from . import cache

@cache.cached(timeout=3600, key_prefix='get_appliance_serial')
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

@cache.cached(timeout=3600, key_prefix='get_external_url')
def get_external_url(dashboard, org_id, network_id):
    """
    Get the external URL of the appliance.
    """
    try:
        serial = get_appliance_serial(dashboard, network_id)
        if serial:
            interface = dashboard.devices.getDeviceManagementInterface(serial)
            return interface.get('ddnsHostnames', {}).get('activeDdnsHostname', 'Not available')
        return "Appliance not found"
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting external URL: {e}")
        return None

@cache.cached(timeout=300, key_prefix='verify_port_forwarding_rule')
def verify_port_forwarding_rule(dashboard, network_id):
    """
    Verify that the port forwarding rule is active.
    """
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallPortForwardingRules(network_id)
        for rule in rules['rules']:
            if rule['name'] == 'Captive Portal':
                return True
        return False
    except meraki.APIError as e:
        logging.error(f"Meraki API error verifying port forwarding rule: {e}")
        return False

@cache.cached(timeout=300, key_prefix='verify_splash_page')
def verify_splash_page(dashboard, network_id, ssid_name):
    """
    Verify that the splash page is set correctly for a given SSID.
    """
    try:
        ssids = dashboard.wireless.getNetworkWirelessSsids(network_id)
        for ssid in ssids:
            if ssid['name'] == ssid_name:
                splash_settings = dashboard.wireless.getNetworkWirelessSsidSplashSettings(network_id, ssid['number'])
                external_url = get_external_url(dashboard, os.environ.get('MERAKI_ORG_ID'), network_id)
                external_port = os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001))
                expected_splash_url = f"http://{external_url}:{external_port}/"
                return splash_settings.get('splashUrl') == expected_splash_url
        return False
    except meraki.APIError as e:
        logging.error(f"Meraki API error verifying splash page: {e}")
        return False

def add_port_forwarding_rule(dashboard, network_id):
    """
    Add a port forwarding rule to the appliance to forward traffic to the captive portal.
    """
    lan_ip = os.environ.get('LAN_IP')
    if not lan_ip:
        logging.error("LAN_IP environment variable not set, cannot add port forwarding rule.")
        return

    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallPortForwardingRules(network_id)
        new_rule = {
            'name': 'Captive Portal',
            'lanIp': lan_ip,
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

def add_firewall_rule(dashboard, network_id):
    """
    Add a firewall rule to the appliance to allow traffic to the captive portal.
    """
    try:
        rules = dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules(network_id)
        new_rule = {
            'comment': 'Allow traffic to captive portal',
            'policy': 'allow',
            'protocol': 'tcp',
            'destPort': os.environ.get('EXTERNAL_PORT', os.environ.get('PORT', 5001)),
            'destCidr': 'any',
            'srcCidr': 'any',
            'srcPort': 'any'
        }
        rules['rules'].insert(0, new_rule)
        dashboard.appliance.updateNetworkApplianceFirewallL3FirewallRules(network_id, rules=rules['rules'])
        logging.info("Firewall rule added successfully")
    except meraki.APIError as e:
        logging.error(f"Meraki API error adding firewall rule: {e}")

def update_splash_page_settings(dashboard, org_id, ssid_names):
    """
    Update the splash page settings for the given SSIDs.
    """
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
                    external_url = get_external_url(dashboard, org_id, network['id'])
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

def get_meraki_clients():
    """
    Get all clients from all networks in the organization.
    """
    dashboard = get_dashboard()
    org_id = os.environ.get('MERAKI_ORG_ID')
    if not dashboard or not org_id:
        return []

    try:
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        clients = []
        for network in networks:
            clients.extend(dashboard.networks.getNetworkClients(network['id'], timespan=86400))
        return clients
    except meraki.APIError as e:
        logging.error(f"Meraki API error getting clients: {e}")
        return []
