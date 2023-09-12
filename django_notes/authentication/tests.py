from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . tokens import generate_token

class AuthenticationViewsTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test@example.com',
            'password': 'testpassword',
            'verifypassword': 'testpassword',
        }
        
    def test_signup_view(self):
        response = self.client.get(reverse('signup')) 
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('signup'), data=self.user_data)
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())
        user = User.objects.get(username=self.user_data['username'])
        self.assertFalse(user.is_active)
        
    def test_signin_view(self):
        User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('signin'), data={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)

        self.assertIn('_auth_user_id', self.client.session)
        
    def test_activate_view(self):
        user = User.objects.create_user(username=self.user_data['username'], password=self.user_data['password'])
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = generate_token.make_token(user)
        activation_url = reverse('activate', args=[uidb64, token])

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 302) 

        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.is_active)