import unittest
from app import create_app, db
from app.models import User, Profile
from flask import url_for

class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(username='test@example.com')
        self.user.set_password('password')
        self.profile = Profile()
        self.user.profile = self.profile
        db.session.add(self.user)
        db.session.add(self.profile)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post(url_for('routes.login'), data={
            'username': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)

    def test_profile_page(self):
        with self.app.test_request_context():
            self.login()
            response = self.client.get(url_for('routes.profile'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Profile', response.data)

    def test_update_profile(self):
        with self.app.test_request_context():
            self.login()
            response = self.client.post(url_for('routes.profile'), data={
                'dark_mode': True
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.user.profile.dark_mode)
