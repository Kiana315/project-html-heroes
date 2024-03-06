from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from SocialDistribution.models import Like, Post, User, Comment, Friend
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


class CommentAPITests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', email='test1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='user2', email='test2@example.com', password='testpassword')
        self.user3 = User.objects.create_user(username='user3', email='test3@example.com', password='testpassword')
        
        # Login user1
        self.client.login(username='user1', password='testpassword')
        
        # Create test posts
        self.post_public = Post.objects.create(author=self.user1, title='Public Post', content='Public Content', visibility='PUBLIC')
        self.post_friends = Post.objects.create(author=self.user1, title='Friends Only Post', content='Friends content', visibility='FRIENDS')
        
        # Login user2 and user3
        self.client.login(username='user2', password='testpassword')
        self.client.login(username='user3', password='testpassword')
        
        # Create friend relationships
        Friend.objects.create(user1=self.user1, user2=self.user2)
        Friend.objects.create(user1=self.user2, user2=self.user1)
        
        # Verify friend relationships
        is_friends_1_to_2 = Friend.objects.filter(user1=self.user1, user2=self.user2).exists()
        is_friends_2_to_1 = Friend.objects.filter(user1=self.user2, user2=self.user1).exists()
        print("User1 and User2 are friends:", is_friends_1_to_2)
        print("User2 and User1 are friends:", is_friends_2_to_1)


    def test_get_comments_for_public_post(self):
        # Get comment list
        url = reverse('API_PComms', kwargs={'post_id': self.post_public.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_on_public_post(self):
        # test comment on public post
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user2.key)
        url = reverse('API_PComms', kwargs={'post_id': self.post_public.id})
        data = {'comment_text': 'A public comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_on_friends_post_as_friend(self):
        # comment as a friend
        self.client.logout()  # make sure clean the login information
        self.client.login(username='user2', password='testpassword')
        url = reverse('API_PComms', kwargs={'post_id': self.post_friends.id})
        data = {'comment_text': 'A friend comment'}
        response = self.client.post(url, data)  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_on_friends_post_not_as_friend(self):
        # test comment as not a friend
        url = reverse('API_PComms', kwargs={'post_id': self.post_friends.id})
        data = {'comment_text': 'An unauthorized comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)