# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from mock import patch

from django.urls import reverse
from django.test import override_settings
from rest_framework import status

from .test import APITestCase

from django_module_users.models import User


class RegisterApiTests(APITestCase):

    def setUp(self):
        self.client = self.client_class()

    def test_register_flow(self):
        url = reverse('register')
        data = {
            'username': 'juan@ripio.com',
            'email': 'juan@ripio.com',
            'password': 'LaPassword1031'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        self.assertTrue('id' in data)
        self.assertTrue('username' in data)
        self.assertTrue('email' in data)
        self.assertTrue('first_name' in data)
        self.assertTrue('last_name' in data)
        self.assertTrue('is_confirmed' in data)
        self.assertTrue('is_staff' in data)
        self.assertTrue('is_active' in data)
        self.assertTrue('type' in data)
        self.assertTrue('roles' in data)
        self.assertTrue('groups' in data)

        user = User.objects.last()
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['is_confirmed'], user.is_confirmed)
        self.assertEqual(data['is_staff'], user.is_staff)
        self.assertEqual(data['is_active'], user.is_active)
        self.assertEqual(data['type'], user.type)
        self.assertEqual(data['roles'], [])
        self.assertEqual(data['groups'], [])

        url = reverse('resend_email')
        data = {
            'email': user.email,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        url = reverse('confirm_email')
        data = {
            'id': user.id,
            'key': user.confirmation_key
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertTrue('id' in data)
        self.assertTrue('username' in data)
        self.assertTrue('email' in data)
        self.assertTrue('first_name' in data)
        self.assertTrue('last_name' in data)
        self.assertTrue('is_confirmed' in data)
        self.assertTrue('is_staff' in data)
        self.assertTrue('is_active' in data)
        self.assertTrue('type' in data)
        self.assertTrue('roles' in data)
        self.assertTrue('groups' in data)

        user = User.objects.last()
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['is_confirmed'], user.is_confirmed)
        self.assertEqual(data['is_confirmed'], True)
        self.assertEqual(data['is_staff'], user.is_staff)
        self.assertEqual(data['is_active'], user.is_active)
        self.assertEqual(data['type'], user.type)
        self.assertEqual(data['roles'], [])
        self.assertEqual(data['groups'], [])

    def test_register_validation(self):
        url = reverse('register')

        # Invalid Data
        data = {
            'email': 'juanripio.com',
            'password': ''
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()

        self.assertEqual(data_validation['password'], ['This field may not be blank.'])
        self.assertEqual(data_validation['username'], ['This field is required.'])
        self.assertEqual(data_validation['email'], ['Enter a valid email address.'])

        # Create
        data = {
            'username': 'juan@ripio.com',
            'email': 'juan@ripio.com',
            'password': 'LaPassword1031'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        # Create Duplicate
        data = {
            'username': 'juan@ripio.com',
            'email': 'juan@ripio.com',
            'password': 'LaPassword1031'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data_validation = response.json()
        self.assertEqual(data_validation['detail'], 'There is already an account created with this email.')

    def test_resend_email_confirmation_validation(self):
        # Create User
        url = reverse('register')
        data = {
            'username': 'juan@ripio.com',
            'email': 'juan@ripio.com',
            'password': 'LaPassword1031'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()

        url = reverse('resend_email')
        # Invalid Data Confirm Email
        data = {
            'email': 'juanripio.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()

        self.assertEqual(data_validation['email'], ['Enter a valid email address.'])

        # Invalid Email
        data = {
            'email': 'juanXXX@ripio.com',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_email_validation(self):
        # Create User
        url = reverse('register')
        data = {
            'username': 'juan@ripio.com',
            'email': 'juan@ripio.com',
            'password': 'LaPassword1031'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        user = User.objects.last()

        url = reverse('confirm_email')
        # Invalid Data
        data = {
            'key': user.confirmation_key
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()

        self.assertEqual(data_validation['id'], ['This field is required.'])

        # Invalid Key
        data = {
            'id': user.id,
            'key': '111111',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()
        self.assertEqual(data_validation, ['Invalid validation code.'])


class MeApiTests(APITestCase):

    def setUp(self):
        self.user = self.user_factory.create(is_staff=True, password="123456")
        self.client = self.client_class()
        self.client.login(username=self.user.username, password="123456")

    def test_me(self):
        url = reverse('user_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertTrue('id' in data)
        self.assertTrue('username' in data)
        self.assertTrue('email' in data)
        self.assertTrue('first_name' in data)
        self.assertTrue('last_name' in data)
        self.assertTrue('is_confirmed' in data)
        self.assertTrue('is_staff' in data)
        self.assertTrue('is_active' in data)
        self.assertTrue('type' in data)
        self.assertTrue('roles' in data)
        self.assertTrue('groups' in data)

        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertEqual(data['is_confirmed'], self.user.is_confirmed)
        self.assertEqual(data['is_staff'], self.user.is_staff)
        self.assertEqual(data['is_active'], self.user.is_active)
        self.assertEqual(data['type'], self.user.type)
        self.assertEqual(data['roles'], [])
        self.assertEqual(data['groups'], [])

    def test_me_no_token(self):
        self.client.logout()

        url = reverse('user_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_update(self):
        url = reverse('user_me')
        data = {
            'email': 'cualqueirda',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'is_staff': False,
            'type': 'APP',
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_rta = response.json()

        self.assertTrue('id' in data_rta)
        self.assertTrue('username' in data_rta)
        self.assertTrue('email' in data_rta)
        self.assertTrue('first_name' in data_rta)
        self.assertTrue('last_name' in data_rta)
        self.assertTrue('is_confirmed' in data_rta)
        self.assertTrue('is_staff' in data_rta)
        self.assertTrue('is_active' in data_rta)
        self.assertTrue('type' in data_rta)
        self.assertTrue('roles' in data_rta)
        self.assertTrue('groups' in data_rta)

        self.user.refresh_from_db()
        self.assertEqual(data_rta['id'], self.user.id)
        self.assertEqual(data_rta['username'], self.user.username)
        self.assertEqual(data_rta['email'], self.user.email)
        self.assertEqual(data_rta['first_name'], self.user.first_name)
        self.assertEqual(data_rta['last_name'], self.user.last_name)
        self.assertEqual(data_rta['is_confirmed'], self.user.is_confirmed)
        self.assertEqual(data_rta['is_staff'], self.user.is_staff)
        self.assertEqual(data_rta['is_active'], self.user.is_active)
        self.assertEqual(data_rta['type'], self.user.type)
        self.assertEqual(data_rta['roles'], [])
        self.assertEqual(data_rta['groups'], [])

        self.assertNotEqual(data_rta['username'], data['email'])
        self.assertNotEqual(data_rta['email'], data['email'])
        self.assertEqual(data_rta['first_name'], data['first_name'])
        self.assertEqual(data_rta['last_name'], data['last_name'])
        self.assertEqual(data_rta['is_staff'], self.user.is_staff)
        self.assertEqual(data_rta['type'], data['type'])

    def test_me_update_validation(self):
        url = reverse('user_me')

        # Invalid data
        data = {
            'first_name': 'Juan',
            'last_name': 'Perez',
            'type': 'APP_2',
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()
        self.assertEqual(data_validation['type'], ['"APP_2" is not a valid choice.'])

    def test_me_update_no_token(self):
        self.client.logout()

        data = {
            'first_name': 'Juan',
            'last_name': 'Perez',
        }
        url = reverse('user_me')
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_email_update(self):
        self.assertEqual(self.user.is_confirmed, True)

        url = reverse('change_email')
        data = {
            'email': 'pepe@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'pepe@gmail.com')
        self.assertEqual(self.user.email, 'pepe@gmail.com')
        self.assertEqual(self.user.is_confirmed, False)

    def test_change_email_validation(self):
        url = reverse('change_email')

        # Invalid data
        data = {
            'email': 'sadasds',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()
        self.assertEqual(data_validation['password'], ['This field is required.'])
        self.assertEqual(data_validation['email'], ['Enter a valid email address.'])

        self.user_factory.create(username="pepe@gmail.com", email="pepe@gmail.com", password="123456")

        data = {
            'email': 'pepe@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()
        self.assertEqual(data_validation['email'], ['Email not available.'])

    def test_change_email_no_token(self):
        self.client.logout()

        data = {
            'email': 'pepe@gmail.com',
            'password': '123456'
        }
        url = reverse('change_email')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_update(self):
        self.assertEqual(self.user.is_confirmed, True)

        url = reverse('change_password')
        data = {
            'actual_password': '123456',
            'new_password': 'PasswordComple123'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_validation(self):
        url = reverse('change_password')

        # Invalid data
        data = {
            'new_password': 'simple'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data_validation = response.json()
        self.assertEqual(data_validation['actual_password'], ['This field is required.'])
        self.assertEqual(
            data_validation['new_password'],
            ['This password is too short. It must contain at least 8 characters.'])

    def test_change_password_no_token(self):
        self.client.logout()

        data = {
            'email': 'pepe@gmail.com',
            'password': '123456'
        }
        url = reverse('change_password')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)