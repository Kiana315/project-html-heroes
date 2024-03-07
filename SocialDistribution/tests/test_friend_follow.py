#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from SocialDistribution.models import User, Follower, Following


class FriendFollowAPITests(APITestCase):
    def setUp(self):
        # Create two test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.client.login(username='user1', password='password1')

    def test_follow_user(self):
        # Test following a user
        data = {'selfUsername': self.user1.username, 'targetUsername': self.user2.username}
        url = reverse('API_POSTFollowerOf', kwargs=data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user2.refresh_from_db()
        self.assertTrue(self.user2.followers.filter(pk=self.user1.pk).exists())

    def test_unfollow_user(self):
        # Test unfollowing a user
        data = {'selfUsername': self.user1.username, 'targetUsername': self.user2.username}
        url = reverse('API_DELETEFollowerOf', kwargs=data)
        # The user1 should follow user2 first to unfollow later
        self.user2.followers.add(Follower.objects.create(user=self.user2, follower=self.user1))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user2.followers.filter(pk=self.user1.pk).exists())

    def test_get_followers(self):
        # Test getting list of followers for a user
        url = reverse('API_GETFollowers', kwargs={'username': self.user2.username})  # Assume this is the correct URL name
        # The user1 should follow user2 to have a non-empty followers list
        self.user2.followers.add(Follower.objects.create(user=self.user2, follower=self.user1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user1.username, [follower['follower']['username'] for follower in response.data])

    def test_get_following(self):
        # Test getting list of following for a user
        url = reverse('API_GETFollowing', kwargs={'username': self.user1.username})  # Assume this is the correct URL name
        # The user1 should follow user2 to have a non-empty following list
        self.user1.following.add(Following.objects.create(user=self.user1, following=self.user2))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2.username, [followee['following']['username'] for followee in response.data])
