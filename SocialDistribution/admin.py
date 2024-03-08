from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'bio')
    search_fields = ('username', 'email')


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'last_modified')
    search_fields = ('title', 'content')
    list_filter = ('date_posted', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('commenter', 'date_commented', 'comment_text')
    list_filter = ('date_commented', 'commenter')


class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'liker', 'date_liked')
    list_filter = ('date_liked', 'liker')


class FollowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'following', 'date_followed')
    list_filter = ('date_followed',)
    search_fields = ('user__username', 'following__username',)


class FollowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower', 'date_followed')
    list_filter = ('date_followed',)
    search_fields = ('user__username', 'follower__username',)


class FriendAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'date_became_friends')
    list_filter = ('date_became_friends',)
    search_fields = ('user1__username', 'user2__username',)
    actions = ['remove_following_follower_relationships']
    def remove_following_follower_relationships(self, request, queryset):
        for friendship in queryset:
            Following.objects.filter(user=friendship.user1, following=friendship.user2).delete()
            Following.objects.filter(user=friendship.user2, following=friendship.user1).delete()
            Follower.objects.filter(user=friendship.user1, follower=friendship.user2).delete()
            Follower.objects.filter(user=friendship.user2, follower=friendship.user1).delete()
    remove_following_follower_relationships.short_description = "Following & follower removed for a new friendship"


class MessageAdmin(admin.ModelAdmin):
    list_display = ('owner', 'date', 'message_type', 'content', 'origin')
    list_filter = ('message_type', 'date')
    search_fields = ('content', 'owner__username', 'origin')
    ordering = ('-date',)

    actions = ['filter_messages_by_type']


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Following, FollowingAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(MessageSuper, MessageAdmin)


