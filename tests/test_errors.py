import unittest
from app import create_app, db

class ErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_404_error(self):
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'File Not Found', response.data)

    def test_500_error(self):
        self.app.config['TESTING'] = False
        @self.app.route('/test-500')
        def test_500():
            raise Exception('Test Exception')
        response = self.client.get('/test-500')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'An unexpected error has occurred', response.data)
