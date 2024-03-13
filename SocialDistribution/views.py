# Traditional Pattern:
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
import base64

# REST Pattern:
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied

# Project Dependencies:
from .serializers import *
from .forms import *
from .permissions import IsAuthorOrReadOnly
from .models import *

User = get_user_model()

"""
---------------------------------- Signup/Login Settings ----------------------------------
"""


class LoginView(LoginView):
    template_name = 'login.html'


def signupView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if password == confirm_password:
            # user existence check
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return render(request, 'signup.html')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return render(request, 'signup.html')
            else:
                # create new account
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('PAGE_Login')
        else:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


"""
---------------------------------- Posts Presentation Settings ----------------------------------
"""


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)

        # def get_context_data(self, **kwargs):

    #     context = super().get_context_data(**kwargs)
    #     post = self.get_object()
    #     context['likes_count'] = Like.objects.filter(post=post).count()
    #     return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            post = self.get_object()
            data = {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'image_url': post.image.url if post.image else '',
                'likes_count': Like.objects.filter(post=post).count(),
                'comments': list(post.get_comments().values('user__username', 'text')),
            }
            return JsonResponse(data)
        else:
            context['likes_count'] = Like.objects.filter(post=self.get_object()).count()
            return super().render_to_response(context, **response_kwargs)



class IndexView(TemplateView):
    """ * [GET] Get The Home/PP Page """
    template_name = "index.html"


class FriendPostsView(TemplateView):
    """ * [GET] Get The FP Page """
    template_name = "friendPosts.html"


class PPsAPIView(generics.ListAPIView):
    """ [GET] Get The Public Posts """
    serializer_class = PostSerializer

    def get_queryset(self):
        # Get all public posts，sorted by publication time in descending order
        return Post.objects.filter(visibility='PUBLIC', is_draft=False).order_by('-date_posted')


class FPsAPIView(generics.ListAPIView):
    """ [GET] Get The Username-based Friend Posts """
    def get(self, request, username):
        current_user = get_object_or_404(User, username=username)   # get current user

        # Query the users followed by the current user
        user_following = User.objects.filter(reverse_following__user=current_user)
        # Get query set of public posts from following users
        user_following_posts = Post.objects.filter(author__in=user_following, visibility='PUBLIC', is_draft=False)

        # Get query set of current user's friend list  
        friends = User.objects.filter(friends_set1__user1=current_user).values_list('friends_set1__user2', flat=True)


        # Get query set of friends’ public and friends-only posts
        friend_posts = Post.objects.filter(
            Q(author__in=friends, visibility='PUBLIC') |
            Q(author__in=friends, visibility='FRIENDS'), is_draft=False
        )

        # Get query set of current user's PUBLIC and FRIENDS posts
        user_posts = Post.objects.filter(
            Q(author=current_user, visibility='PUBLIC') |
            Q(author=current_user, visibility='FRIENDS'), is_draft=False
        )

        # Merge query sets and remove duplicates
        posts = user_following_posts | friend_posts | user_posts
        posts = posts.distinct().order_by('-date_posted')
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class NPsAPIView(generics.CreateAPIView):
    """ [POST] Create A New Post """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # set current user as author


class DeletePostView(APIView):
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            post.delete()
            return Response({"status": "success"}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePostView(APIView):
    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
---------------------------------- Posts Update/Interaction Settings ----------------------------------
"""


# class PostDetailAPIView(generics.CreateAPIView):
#   """ * [GET] Get The Post Detail """
#   template_name = "post_detail.html"


def author_draft_view(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'user': user,
        'posts': Post.objects.filter(author=user, is_draft=True).order_by('-date_posted')
    }
    return render(request, 'author_draft.html', context)


class PostOperationAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ [GET/PUT/DELETE] Get, Update, or Delete A Specific Post """
    queryset = Post.objects.all()
    serializer_class = PostSerializer   
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)


class CommentAPIView(generics.ListCreateAPIView):
    """ [GET/POST] Get The CommentList For A Spec-post; Create A Comment For A Spec-post """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        user = self.request.user

        # If the post is friends-only, filter comments
        if post.visibility == 'FRIENDS':
            friends = User.objects.filter(
                Q(friends_set1__user2=post.author) | 
                Q(friends_set2__user1=post.author)
            ).distinct()
            
            # Check if the user is a friend or the author of the post
            if user in friends or user == post.author:
                return Comment.objects.filter(post=post)
            else:
                # If not a friend or the author, the user should not see any comments
                return Comment.objects.none()

        # If the post is public, return all comments
        return Comment.objects.filter(post=post)

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        user = self.request.user

        if post.visibility == 'FRIENDS' and not post.author.is_friend(user) and user != post.author:
            raise PermissionDenied('You do not have permission to comment on this post.')

        comment = serializer.save(post=post, commenter=user)

        MessageSuper.objects.create(
            post=post,
            owner=post.author,
            message_type='CM',  # 'CM' for comment
            content=f'{user.username} commented on your post: "{comment.comment_text}"',
            origin=user.username 
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class LikeAPIView(generics.ListCreateAPIView):
    """ [GET/POST] Get The LikeList For A Spec-post; Create A Like For A Spec-post """
    serializer_class = LikeSerializer

    # def get_queryset(self):
    #     return get_list_or_404(Like, post_id=self.kwargs['post_id'])
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Like.objects.filter(post_id=post_id)


    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        user = self.request.user
        if Like.objects.filter(post=post, liker=user).exists():
            # raise ValidationError('You have already liked this post.')
            raise DRFValidationError('You have already liked this post.')
        serializer.save(post=post, liker=user)

        message_content = f'{user.username} liked your post "{post.title}".'
        MessageSuper.objects.create(
            owner=post.author,
            message_type='LK',  
            content=message_content,
            origin=user.username,
            post=post
        )

        post.refresh_from_db()
        likes_count = post.like.count()
        response_data = {
            'likes_count': likes_count,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


def check_like_status(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    has_liked = Like.objects.filter(post=post, liker=user).exists()

    return JsonResponse({'has_liked': has_liked})


class SharePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        original_post = get_object_or_404(Post, pk=post_id)
        original_author_username = original_post.author.username

        profile_url = reverse('PAGE_Profile', kwargs={'username': original_author_username})

        if original_post.visibility != 'PUBLIC':
            raise PermissionDenied('This post cannot be shared as it is not public.')

        if original_post.shared_post is None:
            mention_link = f'<a href="{profile_url}">@{original_author_username}</a>'
            content_with_mention = f"{mention_link}: {original_post.content}"
            repost_title = f"Repost: {original_post.title}"
        else:
            content_with_mention = original_post.content
            repost_title = original_post.title

        new_post = Post.objects.create(
            author=request.user,
            title=repost_title,
            content=content_with_mention,
            image=original_post.image,
            shared_post=original_post,
            # Add other necessary fields...
        )

        shared_content = f"{request.user.username} shared a post: {original_post.title}"

        if original_post.visibility == 'PUBLIC':
            # Send the post notification to all followers
            followers = User.objects.filter(reverse_followers__user=original_post.author)

            friends = User.objects.filter(
                Q(friends_set1__user2=original_post.author) | 
                Q(friends_set2__user1=original_post.author)
            ).distinct()
            all_receivers = followers.union(friends, all=True)

            print(all_receivers)
            for receiver in all_receivers:
                MessageSuper.objects.create(
                    owner=receiver,
                    message_type='NP',  # 'NP' for new post
                    content=shared_content,
                    origin=request.user.username,
                    post=original_post
                )

        return Response({'success': True, 'post_id': new_post.pk}, status=status.HTTP_201_CREATED)

        # elif original_post.visibility == 'FRIENDS':
        #     # Send the post notification to all friends
            # friends = User.objects.filter(
            #     Q(friends_set1__user2=original_post.author) | Q(friends_set2__user1=original_post.author)
            # ).distinct()
            # for friend in friends:
            #     MessageSuper.objects.create(
            #         owner=friend,
            #         message_type='NP',  # 'NP' for new post
            #         content=shared_content,
            #         origin=request.user.username,
            #         post=original_post
            #     )


"""
---------------------------------- Message Inbox Settings ----------------------------------
"""


class InboxView(TemplateView):
    """ * [GET] Get The Inbox Page """
    template_name = "inbox.html"


class MsgsAPIView(generics.ListAPIView):
    """ [GET] Get The Inbox Messages """
    queryset = Post.objects.all()
    serializer_class = PostSerializer


"""
----------------------------------  Profile & Identity Settings ----------------------------------
"""

class ProfileView(TemplateView):
    """ * [GET] Get The FollowerList Page """
    template_name = "profile.html"


def upload_avatar(request, username):
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    return redirect("PAGE_Profile", username=username)


def update_bio(request, username):
    if request.method == 'POST':
        form = UpdateBioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

    return redirect("PAGE_Profile", username=username)


def update_username(request, username):
    if request.method == 'POST':
        form = UpdateUserNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            return JsonResponse({'error': form.errors}, safe=False)

        return JsonResponse({'error': ''}, safe=False)

def update_github_username(request, username):
    github_username = request.user.github_username
    return render(request, 'updateGithub.html', {'github_username': github_username})

def update_github_username_submit(request, username):
    if request.method == 'POST':
        github_username = request.POST.get('github_username')
        # Update the GitHub username in the database (assuming you have a UserProfile model)
        request.user.github_username = github_username
        request.user.save()
        return redirect('PAGE_Profile', username=request.user.username)  # Redirect to the profile page
    return redirect('update_github_username')  # Redirect back to the update page if not POST method

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        profile_user = get_object_or_404(User, username=username)
        current_user = request.user
        print("current_user:", current_user, "\nprofile_user", profile_user)

        if current_user == profile_user:
            # Current user views own posts: Return all posts
            posts = Post.objects.filter(author=profile_user, is_draft=False).order_by('-date_posted')
        elif Friend.objects.filter(user1=current_user, user2=profile_user).exists() or \
             Friend.objects.filter(user1=profile_user, user2=current_user).exists():
            # The current user is friends with the profile user: return public and friend-only posts
            posts = Post.objects.filter(author=profile_user, visibility__in=['PUBLIC', 'FRIENDS'], is_draft=False).order_by('-date_posted')
        else:
            # Other users: only public posts returned
            posts = Post.objects.filter(author=profile_user, visibility='PUBLIC', is_draft=False).order_by('-date_posted')

        user_serializer = UserSerializer(profile_user)
        posts_serializer = PostSerializer(posts, many=True)

        return Response({
            'user': user_serializer.data,
            'posts': posts_serializer.data
        })




def otherProfileView(request, selfUsername, targetUsername):
    selfUser = get_object_or_404(User, username=selfUsername)
    targetUser = get_object_or_404(User, username=targetUsername)

    context = {
        'user': targetUser,
        'posts': Post.objects.filter(author=targetUser).order_by('-date_posted')
    }
    return render(request, 'otherProfile.html', context)


class UsersAPIView(viewsets.ModelViewSet):
    """ [GET] Get The Profile Info """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserAPIView(generics.RetrieveAPIView):
    """ [GET] Get The Profile Info """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_object(self):
        queryset = self.get_queryset()
        username = self.kwargs.get('username')
        obj = get_object_or_404(queryset, username=username)
        return obj


def search_user(request):
    query = request.GET.get('q', '')  # Get search query parameters
    current_user = request.user.username

    try:
        user = User.objects.get(username=query)
        # Or use eamil search：User.objects.get(email=query)
        # Returns a URL pointing to the user's profile
        return JsonResponse({'url': f'/profile/{user.username}/'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


"""
---------------------------------- Friend System Settings ----------------------------------
"""


class FollowerView(TemplateView):
    """ * [GET] Get The FollowerList Page """
    template_name = "followersList.html"


class FollowingView(TemplateView):
    """ * [GET] Get The FollowingList Page """
    template_name = "followingList.html"


class FriendView(TemplateView):
    """ * [GET] Get The FollowingList Page """
    template_name = "friendList.html"


class FollowersAPIView(generics.ListAPIView):
    """ [GET] Get The FollowerList For A Spec-username """
    serializer_class = FollowerSerializer
    def get_queryset(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user.followers.all()


class FollowingAPIView(generics.ListAPIView):
    """ [GET] Get The FollowingList For A Spec-username """
    serializer_class = FollowingSerializer
    def get_queryset(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user.following.all()


class FriendsAPIView(generics.ListAPIView):
    """ [GET] Get The FriendsList For A Spec-username """
    serializer_class = FriendSerializer
    def get_queryset(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return Friend.objects.filter(Q(user1=user) | Q(user2=user)).distinct()


class CreateFollowerAPIView(APIView):
    """ [POST] Create New Follower Relation Case  """
    def post(self, request, selfUsername, targetUsername):
        # Get both users based on their usernames
        self_user = get_object_or_404(User, username=selfUsername)
        target_user = get_object_or_404(User, username=targetUsername)

        if self_user != target_user:
            try:
                Follower.objects.create(user=target_user, follower=self_user)
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"detail": "Already followed by this user."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Cannot add yourself as a follower."}, status=status.HTTP_400_BAD_REQUEST)


class CreateFollowingAPIView(APIView):
    """ [POST] Create New Following Relation Case """
    def post(self, request, selfUsername, targetUsername):
        # Get both users based on their usernames
        self_user = get_object_or_404(User, username=selfUsername)
        target_user = get_object_or_404(User, username=targetUsername)
        if self_user != target_user:
            try:
                Following.objects.create(user=target_user, following=self_user)
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"detail": "Already following."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFollowerAPIView(APIView):
    """ [DELETE] Delete Follower Relation Case """
    def delete(self, request, selfUsername, targetUsername):
        # Get both users based on their usernames
        self_user = get_object_or_404(User, username=selfUsername)
        target_user = get_object_or_404(User, username=targetUsername)

        if self_user != target_user:
            try:
                Follower.objects.filter(user=target_user, follower=self_user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"detail": "An error occurred while deleting the follower relation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail": "Cannot remove yourself as a follower."}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFollowingAPIView(APIView):
    """ [DELETE] Delete Following Relation Case """
    def delete(self, request, selfUsername, targetUsername):
        # Get both users based on their usernames
        self_user = get_object_or_404(User, username=selfUsername)
        target_user = get_object_or_404(User, username=targetUsername)

        if self_user != target_user:
            try:
                Following.objects.filter(user=target_user, following=self_user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"detail": "An error occurred while deleting the following relation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail": "Cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def createFriendshipAPIView(request, selfUsername, targetUsername):
    """ [POST] Post New Friend Relation Case """
    user1 = get_object_or_404(User, username=selfUsername)
    user2 = get_object_or_404(User, username=targetUsername)
    if user1 == user2:
        return JsonResponse({'error': 'A user cannot befriend themselves.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        Friend.create_friendship(user1, user2)
        return JsonResponse({'message': 'Friendship created successfully.'}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def deleteFriendshipAPIView(request, selfUsername, targetUsername):
    """ [DELETE] Delete Friend Relation Case """
    user1 = get_object_or_404(User, username=selfUsername)
    user2 = get_object_or_404(User, username=targetUsername)
    if user1 == user2:
        return JsonResponse({'error': 'A user cannot unfriend themselves.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        Friend.delete_friendship_for_user1(user1, user2)
        return JsonResponse({'message': 'Friendship deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyzeRelationAPIView(APIView):
    """ [GET] Get The Relationship Between Two Users """
    def get(self, request, username1, username2):
        user1 = get_object_or_404(User, username=username1)
        user2 = get_object_or_404(User, username=username2)

        user1_follows_user2 = Following.objects.filter(user=user1, following=user2).exists()
        user2_follows_user1 = Following.objects.filter(user=user2, following=user1).exists()
        user1_followed_by_user2 = Follower.objects.filter(user=user1, follower=user2).exists()
        user2_followed_by_user1 = Follower.objects.filter(user=user2, follower=user1).exists()

        user1_makeFriend_user2 = Friend.objects.filter(user1=user1, user2=user2).exists()
        user2_makeFriend_user1 = Friend.objects.filter(user1=user2, user2=user1).exists()

        data = {
            'user1_follows_user2': user1_follows_user2,
            'user2_follows_user1': user2_follows_user1,
            'user1_followed_by_user2': user1_followed_by_user2,
            'user2_followed_by_user1': user2_followed_by_user1,
            'already_friend': user1_makeFriend_user2 and user2_makeFriend_user1,
            'mutual_follow': user1_follows_user2 and user2_follows_user1 and user1_followed_by_user2 and user2_followed_by_user1,
        }
        return Response(data)


"""
---------------------------------- Inbox Message Settings ----------------------------------
"""


class UserMessagesAPIView(ListAPIView):
    serializer_class = MessageSuperSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        message_type = self.kwargs['type']
        return MessageSuper.objects.filter(owner=user, message_type=message_type)


class CreateMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = MessageSuperSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTypeOfMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, type, format=None):
        MessageSuper.objects.filter(owner=request.user, message_type=type).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteIDOfMessageAPIView(APIView):
    def delete(self, request, ID):
        message = get_object_or_404(MessageSuper, pk=ID, owner=request.user)
        message.delete()

        return JsonResponse({'status': 'success', 'message': f'Message with id={ID} is deleted.'})
