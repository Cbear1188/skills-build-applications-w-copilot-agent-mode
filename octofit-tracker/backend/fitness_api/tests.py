from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import ActivityLog, Profile


class FitnessApiTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='octouser',
			password='testpass123',
		)
		self.profile = self.user.profile
		self.profile.display_name = 'Octo Athlete'
		self.profile.team_name = 'Tentacle Trainers'
		self.profile.weekly_goal_minutes = 180
		self.profile.save()
		self.activity = ActivityLog.objects.create(
			user=self.user,
			activity_type=ActivityLog.RUN,
			duration_minutes=30,
			calories_burned=320,
			activity_date='2026-04-15',
			notes='Tempo session',
		)
		self.token = Token.objects.create(user=self.user)

	def authenticate(self):
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

	def test_api_root_returns_base_metadata(self):
		response = self.client.get(reverse('api-root'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['message'], 'OctoFit Tracker API')
		self.assertIn('base_url', response.data)

	def test_profile_is_auto_created_for_new_user(self):
		self.assertTrue(Profile.objects.filter(user=self.user).exists())

	def test_profile_list_returns_string_identifier(self):
		self.authenticate()
		response = self.client.get('/api/profiles/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0]['id'], str(self.profile.id))
		self.assertEqual(response.data[0]['user'], str(self.user.id))

	def test_activity_list_returns_string_identifier(self):
		self.authenticate()
		response = self.client.get('/api/activities/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0]['id'], str(self.activity.id))
		self.assertEqual(response.data[0]['user'], str(self.user.id))

	def test_register_creates_user_profile_and_token(self):
		response = self.client.post(
			'/api/auth/register/',
			{
				'username': 'newuser',
				'email': 'newuser@example.com',
				'password': 'strongpass123',
				'password_confirm': 'strongpass123',
				'display_name': 'New Octo',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['user']['username'], 'newuser')
		self.assertEqual(response.data['profile']['display_name'], 'New Octo')
		self.assertIn('token', response.data)

	def test_login_returns_existing_token_and_profile(self):
		response = self.client.post(
			'/api/auth/login/',
			{
				'username': 'octouser',
				'password': 'testpass123',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['token'], self.token.key)
		self.assertEqual(response.data['profile']['display_name'], 'Octo Athlete')

	def test_current_user_endpoint_returns_authenticated_user(self):
		self.authenticate()
		response = self.client.get('/api/auth/me/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['user']['username'], 'octouser')

	def test_logout_deletes_token(self):
		self.authenticate()
		response = self.client.post('/api/auth/logout/')

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Token.objects.filter(user=self.user).exists())
