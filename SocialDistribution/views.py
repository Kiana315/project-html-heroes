# Traditional Pattern:
from django.http import Http404
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.db.models import Q
from django.http import JsonResponse

# REST Pattern:
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied

# Project Dependencies:
from .serializers import *
from .forms import SignUpForm, AvatarUploadForm, UpdateBioForm, UpdateUserNameForm
from .models import Post
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
                return redirect('login')
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


"""
def postView(request, username):
    return render(request, 'post.html')
"""


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
        return Post.objects.filter(visibility='PUBLIC').order_by('-date_posted')


class FPsAPIView(generics.ListAPIView):
    """ [GET] Get The Username-based Friend Posts """
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return self._getFPsForUser(user)

    def _getFPsForUser(self, user):
        # todo: rule needed
        return user.friend_posts.all()


class NPsAPIView(generics.CreateAPIView):
    """ [POST] Create A New Post """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # set current user as author


"""
---------------------------------- Posts Update/Interaction Settings ----------------------------------
"""


# class PostDetailAPIView(generics.CreateAPIView):
#   """ * [GET] Get The Post Detail """
#   template_name = "post_detail.html"


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
        serializer.save(post=post, commenter=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context



class LikeAPIView(generics.ListCreateAPIView):
    """ [GET/POST] Get The LikeList For A Spec-post; Create A Like For A Spec-post """
    serializer_class = LikeSerializer

    def get_queryset(self):
        return get_list_or_404(Like, post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        user = self.request.user
        if Like.objects.filter(post=post, liker=user).exists():
            raise ValidationError('You have already liked this post.')
        serializer.save(post=post, liker=user)
        post.refresh_from_db()
        likes_count = post.like.count()
        response_data = {
            'likes_count': likes_count,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


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


def upload_avatar(request, username):
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()

    return redirect(profileView, username=username)


def update_bio(request, username):
    if request.method == 'POST':
        form = UpdateBioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

    return redirect(profileView, username=username)


def update_username(request, username):
    if request.method == 'POST':
        form = UpdateUserNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            return JsonResponse({'error': form.errors}, safe=False)

        return JsonResponse({'error': ''}, safe=False)


def profileView(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'user': user,
        'posts': Post.objects.filter(author=user).order_by('-date_posted')
    }
    return render(request, 'profile.html', context)


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
    def post(self, request, username):
        new_follower = get_object_or_404(User, username=username)
        if request.user != new_follower:
            try:
                Follower.objects.create(user=request.user, follower=new_follower)
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"detail": "Already followed by this user."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Cannot add yourself as a follower."}, status=status.HTTP_400_BAD_REQUEST)


class CreateFollowingAPIView(APIView):
    """ [POST] Create New Following Relation Case """
    def post(self, request, username):
        user_to_follow = get_object_or_404(User, username=username)
        if request.user != user_to_follow:
            try:
                Following.objects.create(user=request.user, following=user_to_follow)
                return Response(status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"detail": "Already following."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)


"""
class CreateFriendAPIView(APIView):
    def post(self, request, username):
        user_to_befriend = get_object_or_404(User, username=username)
        if request.user != user_to_befriend:
            try:
                Friend.create_friendship(request.user, user_to_befriend)
                return Response(status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Cannot become friends with yourself."}, status=status.HTTP_400_BAD_REQUEST)
"""


@api_view(['POST'])
def createFriendshipAPIView(request, user1_id, user2_id):
    """ [POST] Post New Friend Relation Case """
    user1 = get_object_or_404(User, pk=user1_id)
    user2 = get_object_or_404(User, pk=user2_id)
    if user1_id == user2_id:
        return JsonResponse({'error': 'A user cannot befriend themselves.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        Friend.create_friendship(user1, user2)
        return JsonResponse({'message': 'Friendship created successfully.'}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)