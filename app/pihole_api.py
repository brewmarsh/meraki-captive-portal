import requests
import os

def get_pihole_mappings():
    pihole_api_url = os.environ.get('PIHOLE_API_URL')
    pihole_api_key = os.environ.get('PIHOLE_API_KEY')
    if not pihole_api_url or not pihole_api_key:
        return []

    try:
        response = requests.get(f"{pihole_api_url}?customdns&auth={pihole_api_key}", timeout=5)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"Error getting Pi-hole mappings: {e}")
        return []

def add_pihole_mapping(ip, hostname):
    pihole_api_url = os.environ.get('PIHOLE_API_URL')
    pihole_api_key = os.environ.get('PIHOLE_API_KEY')
    if not pihole_api_url or not pihole_api_key:
        return

    try:
        response = requests.get(f"{pihole_api_url}?customdns&action=add&ip={ip}&domain={hostname}&auth={pihole_api_key}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error adding Pi-hole mapping: {e}")

def delete_pihole_mapping(ip, hostname):
    pihole_api_url = os.environ.get('PIHOLE_API_URL')
    pihole_api_key = os.environ.get('PIHOLE_API_KEY')
    if not pihole_api_url or not pihole_api_key:
        return

    try:
        response = requests.get(f"{pihole_api_url}?customdns&action=delete&ip={ip}&domain={hostname}&auth={pihole_api_key}", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error deleting Pi-hole mapping: {e}")
