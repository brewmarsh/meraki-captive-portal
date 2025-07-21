import unittest
from unittest.mock import patch, MagicMock
from app.meraki_api import get_organization_id, update_splash_page_settings

class TestMerakiApi(unittest.TestCase):

    def test_get_organization_id(self):
        """
        Test that get_organization_id returns the provided organization ID.
        """
        org_id = get_organization_id(None, '123')
        self.assertEqual(org_id, '123')

    @patch('meraki.DashboardAPI')
    def test_update_splash_page_settings(self, mock_dashboard_api):
        """
        Test that update_splash_page_settings calls the correct Meraki API functions.
        """
        mock_dashboard = MagicMock()
        mock_dashboard_api.return_value = mock_dashboard

        mock_dashboard.organizations.getOrganizationNetworks.return_value = [
            {'id': 'net-1', 'name': 'Test Network 1'}
        ]
        mock_dashboard.wireless.getNetworkWirelessSsids.return_value = [
            {'number': 0, 'name': 'Test SSID 1'},
            {'number': 1, 'name': 'Test SSID 2'}
        ]

        with patch.dict('os.environ', {'PUBLIC_IP': '1.2.3.4', 'PORT': '8080'}):
            update_splash_page_settings('fake_key', '123', ['Test SSID 1'])

        mock_dashboard.wireless.updateNetworkWirelessSsidSplashSettings.assert_called_once_with(
            networkId='net-1',
            number=0,
            splashPage='custom',
            splashUrl='http://1.2.3.4:8080/'
        )

if __name__ == '__main__':
    unittest.main()
