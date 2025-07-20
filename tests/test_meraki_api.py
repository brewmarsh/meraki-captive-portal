import unittest
from unittest.mock import patch, MagicMock
from app.meraki_api import get_network_id, update_splash_page_settings

class TestMerakiApi(unittest.TestCase):

    @patch('meraki.DashboardAPI')
    def test_get_network_id_success(self, mock_dashboard_api):
        """
        Test that get_network_id returns the correct organization ID when the organization is found.
        """
        mock_dashboard = MagicMock()
        mock_dashboard.organizations.getOrganizations.return_value = [
            {'id': '123', 'name': 'Test Org'},
            {'id': '456', 'name': 'Another Org'}
        ]
        mock_dashboard_api.return_value = mock_dashboard

        org_id = get_network_id(mock_dashboard, 'Test Org')
        self.assertEqual(org_id, '123')

    @patch('meraki.DashboardAPI')
    def test_get_network_id_not_found(self, mock_dashboard_api):
        """
        Test that get_network_id returns None when the organization is not found.
        """
        mock_dashboard = MagicMock()
        mock_dashboard.organizations.getOrganizations.return_value = [
            {'id': '456', 'name': 'Another Org'}
        ]
        mock_dashboard_api.return_value = mock_dashboard

        org_id = get_network_id(mock_dashboard, 'Test Org')
        self.assertIsNone(org_id)

    @patch('app.meraki_api.get_network_id')
    @patch('meraki.DashboardAPI')
    def test_update_splash_page_settings(self, mock_dashboard_api, mock_get_network_id):
        """
        Test that update_splash_page_settings calls the correct Meraki API functions.
        """
        mock_dashboard = MagicMock()
        mock_dashboard_api.return_value = mock_dashboard
        mock_get_network_id.return_value = '123'

        mock_dashboard.organizations.getOrganizationNetworks.return_value = [
            {'id': 'net-1', 'name': 'Test Network 1'}
        ]
        mock_dashboard.wireless.getNetworkWirelessSsids.return_value = [
            {'number': 0, 'name': 'Test SSID 1'},
            {'number': 1, 'name': 'Test SSID 2'}
        ]

        with patch.dict('os.environ', {'PUBLIC_IP': '1.2.3.4', 'PORT': '8080'}):
            update_splash_page_settings('fake_key', 'Test Org', ['Test SSID 1'])

        mock_dashboard.wireless.updateNetworkWirelessSsidSplashSettings.assert_called_once_with(
            networkId='net-1',
            number=0,
            splashPage='custom',
            splashUrl='http://1.2.3.4:8080/'
        )

if __name__ == '__main__':
    unittest.main()
