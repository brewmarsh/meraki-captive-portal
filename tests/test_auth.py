import unittest
from app import create_app, db
from app.models import User
from flask import url_for

class AuthTestCase(unittest.TestCase):
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

    def test_register(self):
        with self.app.test_request_context():
            response = self.client.post(url_for('routes.register'), data={
                'email': 'test@example.com',
                'password': 'password',
                'password2': 'password'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password'))

    def test_login_logout(self):
        user = User(username='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        with self.app.test_request_context():
            response = self.client.post(url_for('routes.login'), data={
                'username': 'test@example.com',
                'password': 'password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            response = self.client.get(url_for('routes.logout'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
