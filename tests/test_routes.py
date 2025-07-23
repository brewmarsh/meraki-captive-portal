import unittest
from app import create_app, db
from app.models import Client, User
from flask import url_for

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(username='testuser')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        with self.app.test_request_context():
            return self.client.post(url_for('routes.login'), data={
                'username': 'testuser',
                'password': 'password'
            }, follow_redirects=True)

    def test_splash_page_new_client(self):
        """
        Test that the splash page creates a new client.
        """
        self.login()
        response = self.client.get('/?client_mac=00:11:22:33:44:55&client_ip=1.2.3.4&base_grant_url=https://meraki.com')
        self.assertEqual(response.status_code, 200)
        client = Client.query.filter_by(mac_address='00:11:22:33:44:55').first()
        self.assertIsNotNone(client)
        self.assertEqual(client.ip_address, '1.2.3.4')

    def test_splash_page_returning_client(self):
        """
        Test that the splash page updates a returning client.
        """
        self.login()
        client = Client(mac_address='00:11:22:33:44:55', ip_address='1.2.3.4')
        db.session.add(client)
        db.session.commit()
        last_seen_before = client.last_seen
        response = self.client.get('/?client_mac=00:11:22:33:44:55&client_ip=1.2.3.4&base_grant_url=https://meraki.com')
        self.assertEqual(response.status_code, 200)
        client = Client.query.filter_by(mac_address='00:11:22:33:44:55').first()
        self.assertGreater(client.last_seen, last_seen_before)

    def test_splash_page_no_meraki_data(self):
        """
        Test that the splash page handles requests without Meraki data.
        """
        self.login()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Direct access is not supported.', response.data)

    def test_splash_page_timer(self):
        """
        Test that the splash page includes the timer.
        """
        self.login()
        self.app.config['SPLASH_TIMER_SECONDS'] = 15
        response = self.client.get('/?client_mac=00:11:22:33:44:55&client_ip=1.2.3.4&base_grant_url=https://meraki.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'let timeLeft = 15;', response.data)

    def test_connect_with_redirect_url(self):
        """
        Test that the connect route redirects to the URL stored in the session.
        """
        with self.client.session_transaction() as sess:
            sess['redirect_url'] = 'https://www.google.com'
        response = self.client.get('/connect')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.google.com')

    def test_connect_without_redirect_url(self):
        """
        Test that the connect route redirects to the default URL.
        """
        response = self.client.get('/connect')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.reddit.com')

    def test_admin_access_allowed(self):
        """
        Test that admin access is allowed from the correct subnet.
        """
        self.app.config['ADMIN_SUBNET'] = '192.168.1.0/24'
        response = self.client.get('/admin', headers={'X-Forwarded-For': '192.168.1.100'})
        self.assertEqual(response.status_code, 200)

    def test_admin_access_denied(self):
        """
        Test that admin access is denied from the incorrect subnet.
        """
        self.app.config['ADMIN_SUBNET'] = '192.168.1.0/24'
        response = self.client.get('/admin', headers={'X-Forwarded-For': '10.0.0.100'})
        self.assertEqual(response.status_code, 200) # Returns an image, so 200 is expected
        self.assertIn(b'PNG', response.data)

    def test_admin_dashboard(self):
        """
        Test that the admin dashboard displays the correct information.
        """
        client1 = Client(mac_address='00:11:22:33:44:55', ip_address='1.2.3.4', user_agent='test-agent-1')
        client2 = Client(mac_address='AA:BB:CC:DD:EE:FF', ip_address='5.6.7.8', user_agent='test-agent-2')
        db.session.add_all([client1, client2])
        db.session.commit()
        response = self.client.get('/admin', headers={'X-Forwarded-For': '127.0.0.1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<p>2</p>', response.data)
        self.assertIn(b'00:11:22:33:44:55', response.data)
        self.assertIn(b'AA:BB:CC:DD:EE:FF', response.data)

    def test_meraki_status_page(self):
        """
        Test that the Meraki status page is rendered correctly.
        """
        response = self.client.get('/meraki_status')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Meraki Status', response.data)

    def test_loading_screen(self):
        """
        Test that the loading screen is present.
        """
        response = self.client.get('/admin', headers={'X-Forwarded-For': '127.0.0.1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="loader"></div>', response.data)

if __name__ == '__main__':
    unittest.main()
