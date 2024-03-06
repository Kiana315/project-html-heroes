import commonmark
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q



class User(AbstractUser):
    # A text field used to store the user's personal profile.
    #   blank=True indicates that this field is optional
    #   and users can not fill in the introduction when registering
    bio = models.TextField(max_length=200, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    avatar = models.ImageField(upload_to='avatars/', default="avatars/default_avatar.png")

    def is_friend(self, other_user):
        return Friend.objects.filter(
            Q(user1=self, user2=other_user) | Q(user1=other_user, user2=self)
        ).exists()

    @property
    def avatar_url(self):
        return self.avatar.url if self.avatar else ""


class Post(models.Model):
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('FRIENDS', 'Friends-Only'),
        ('PRIVATE', 'Private'),
    ]
    CONTENT_TYPE_CHOICES = [
        ('COMMONMARK', 'CommonMark'),
        ('PLAIN', 'Plain Text'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='PLAIN')
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PUBLIC')
    date_posted = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=False)
    shared_post = models.ForeignKey('self', on_delete=models.CASCADE, related_name='shared_posts', null=True, blank=True)
    ordering = ['-date_posted']

    # def get_html_content(self):
    #     if self.content_type == 'COMMONMARK':
    #         return commonmark.commonmark(self.content)
    #     return self.content

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment', default=99999)
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commenters', default=0)
    date_commented = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField()
    class Meta:
        ordering = ['-date_commented']


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like', default=99999)
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likers', default=0)
    date_liked = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date_liked']


class Following(models.Model):
    user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='reverse_following', on_delete=models.CASCADE)
    date_followed = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'following',)
        ordering = ['-date_followed']


class Follower(models.Model):
    user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='reverse_followers', on_delete=models.CASCADE)
    date_followed = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'follower',)
        ordering = ['-date_followed']


class Friend(models.Model):
    user1 = models.ForeignKey(User, related_name='friends_set1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friends_set2', on_delete=models.CASCADE)
    date_became_friends = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship')]
        ordering = ['-date_became_friends']
    def clean(self):
        if self.user1 == self.user2:
            raise ValidationError("Users cannot be friends with themselves.")
    @classmethod
    def create_friendship(cls, user1, user2):
        if user1 != user2 and not cls.objects.filter(user1=user1, user2=user2).exists():
            Friend.objects.create(user1=user1, user2=user2)
            Friend.objects.create(user1=user2, user2=user1)
            Following.objects.filter(user=user1, following=user2).delete()
            Following.objects.filter(user=user2, following=user1).delete()
            Follower.objects.filter(user=user1, follower=user2).delete()
            Follower.objects.filter(user=user2, follower=user1).delete()
        else:
            raise ValidationError("Cannot create a friendship")
    @classmethod
    def delete_friendship_for_user1(cls, user1, user2):
        if user1 != user2 and cls.objects.filter(user1=user1, user2=user2).exists():
            Friend.objects.filter(user1=user1, user2=user2).delete()
            Friend.objects.filter(user1=user2, user2=user1).delete()
            Following.objects.create(user=user2, following=user1)
            Follower.objects.create(user=user1, follower=user2)
        else:
            raise ValidationError("Cannot delete a friendship")


class Message(models.Model):
    MESSAGE_TYPES = [
        ('FR', 'Follow Request'),
        ('LK', 'Like'),
        ('CM', 'Comment'),
        ('NP', 'New Post Reminder'),
        ('SU', 'New Sign Up')
    ]
    owner = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=2, choices=MESSAGE_TYPES)
    class Meta:
        ordering = ['-date']
    @classmethod
    def get_messages_of_type_for_user(cls, user, message_type):
        return cls.objects.filter(owner=user, message_type=message_type)



