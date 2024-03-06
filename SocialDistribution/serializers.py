from rest_framework import serializers
from .models import *
from django.templatetags.static import static


class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='author.username')
    avatar = serializers.ReadOnlyField(source='author.avatar_url')
    likes_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_draft = serializers.BooleanField(default=False)
    # html_content = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField() 
    shared_post_id = serializers.IntegerField(source='shared_post.id', read_only=True)
    shared_post_title = serializers.CharField(source='shared_post.title', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'username', 'title', 'content', 'content_type', 'image', 'visibility',
            'date_posted', 'last_modified', 'likes_count', 'avatar', 'is_draft',
            'is_shared', 'shared_post_id', 'shared_post_title', 'comment_count'
        ]
        extra_kwargs = {'author': {'read_only': True}}

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_comment_count(self, obj):
        return Like.objects.filter(post=obj).count()
    
    def get_is_shared(self, obj):
        return obj.shared_post is not None



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio']


class CommentSerializer(serializers.ModelSerializer):
    commenter_username = serializers.CharField(source='commenter.username', read_only=True)
    commenter_avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'post', 'commenter', 'commenter_username', 'commenter_avatar_url', 'date_commented', 'comment_text']

    def get_commenter_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.commenter.avatar and hasattr(obj.commenter.avatar, 'url'):
            return request.build_absolute_uri(obj.commenter.avatar.url)
        return request.build_absolute_uri(static('images/post-bg.jpg'))


class LikeSerializer(serializers.ModelSerializer):
    liker_username = serializers.CharField(source='liker.username', read_only=True)
    class Meta:
        model = Like
        fields = ['id', 'post', 'liker', 'liker_username', 'date_liked']


class FollowerSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    class Meta:
        model = Follower
        fields = ['id', 'follower', 'following', 'date_followed']


class FollowingSerializer(serializers.ModelSerializer):
    following = UserSerializer(read_only=True)
    follower = UserSerializer(read_only=True)
    class Meta:
        model = Following
        fields = ['id', 'follower', 'following', 'date_followed']


class FriendSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    class Meta:
        model = Friend
        fields = ['id', 'user1', 'user2', 'date_became_friends']


class MessageSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Message
        fields = ['id', 'owner_username', 'date', 'message_type']
        read_only_fields = ['id', 'date', 'owner_username']
    def create(self, validated_data):
        # Owner will be set in the view, so it's not included in validated_data
        message = Message.objects.create(**validated_data)
        return message