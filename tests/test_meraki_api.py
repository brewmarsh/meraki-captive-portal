import unittest
from unittest.mock import patch, MagicMock
from app.meraki_api import update_splash_page_settings

class TestMerakiApi(unittest.TestCase):

    @patch('app.meraki_api.get_external_url', return_value='1.2.3.4')
    @patch('meraki.DashboardAPI')
    def test_update_splash_page_settings(self, mock_dashboard_api, mock_get_external_url):
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

        with patch.dict('os.environ', {'PORT': '8080'}):
            update_splash_page_settings(mock_dashboard, '123', ['Test SSID 1'])

        mock_dashboard.wireless.updateNetworkWirelessSsidSplashSettings.assert_called_once_with(
            networkId='net-1',
            number=0,
            splashPage='custom',
            splashUrl='http://1.2.3.4:8080/'
        )

if __name__ == '__main__':
    unittest.main()
