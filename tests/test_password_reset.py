import unittest
from app import create_app, db
from app.models import User
from flask import url_for

class PasswordResetTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(username='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_reset_request(self):
        with self.app.test_request_context():
            response = self.client.post(url_for('routes.reset_password_request'), data={
                'email': 'test@example.com'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Check your email', response.data)

    def test_password_reset(self):
        with self.app.test_request_context():
            token = self.user.get_reset_password_token()
            response = self.client.post(url_for('routes.reset_password', token=token), data={
                'password': 'new_password',
                'password2': 'new_password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your password has been reset', response.data)
            self.assertTrue(self.user.check_password('new_password'))
