#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from SocialDistribution.models import User


class UserAPITests(APITestCase):
    def setUp(self):
        # Create two test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.client.login(username='user1', password='password1')

    def test_create_user(self):
        # Test creating a new user
        url = reverse('users-list')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)  # Including the two users from setUp

    def test_get_user_profile(self):
        # Test retrieving a user's profile
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user2')

    def test_update_user_profile(self):
        # Test updating a user's profile
        url = reverse('users-detail', kwargs={'pk': self.user1.pk})
        data = {'username': 'UpdatedName'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'UpdatedName')

    def test_delete_user(self):
        # Test deleting a user
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
