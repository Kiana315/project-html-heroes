from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from SocialDistribution.models import Like, Post, User
from rest_framework.authtoken.models import Token

class LikeAPITests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Create a test post
        self.post = Post.objects.create(author=self.user, title='Test Post', content='Test Content')
        exists = Post.objects.filter(id=self.post.id).exists()
        print("Post exists:", exists, self.post.id)
    
    def test_get_likes_list(self):
        # Get like list
        url = reverse('API_PLikes', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_like_to_post(self):
        # add new like
        url = reverse('API_PLikes', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # account like amounts
        like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(like_count, 1)

    def test_add_like_to_post_duplicate(self):
        url = reverse('API_PLikes', kwargs={'post_id': self.post.id})
        # first like
        self.client.post(url, {})
        # second like
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # confirm like amounts isn't increase
        like_count = Like.objects.filter(post=self.post).count()
        self.assertEqual(like_count, 1)

class CheckLikeStatusTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        print("User created:", hasattr(self, 'user'))
        # Create a test post
        self.post = Post.objects.create(author=self.user, title='Test Post', content='Test Content')
        exists = Post.objects.filter(id=self.post.id).exists()
        print("Post created:", hasattr(self, 'post'))

    def test_check_like_status_not_liked(self):
        # check like status if the user didn't like the post
        self.client.login(username='testuser', password='testpassword')
        url = reverse('check_like_status', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['has_liked'], False)

    def test_check_like_status_liked(self):
        # check like status if the user did like the post
        self.client.login(username='testuser', password='testpassword')
        Like.objects.create(post=self.post, liker=self.user)  # like the post
        url = reverse('check_like_status', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['has_liked'], True)