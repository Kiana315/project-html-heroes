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

# REST Pattern:
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Project Dependencies:
from .serializers import *
from .forms import SignUpForm
from .models import Post
from .permissions import IsAuthorOrReadOnly


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

#class PostDetailAPIView(generics.CreateAPIView):
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
    def get_queryset(self):
        return get_list_or_404(Comment, post_id=self.kwargs['post_id'])
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(post=post, commenter=self.request.user)
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


def profileView(request, username):
    user = get_object_or_404(User, username=username)
    context = {'profile_user': user}
    return render(request, 'profile.html', context)


def followersListView(request, username):
    return render(request, 'peopleList.html')


def followingListView(request, username):
    return render(request, 'peopleList.html')


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


class FollowerAPIView(generics.ListAPIView):
    """ [GET] Get The FollowerList For A Spec-username """
    def get_queryset(self):
        username = self.kwargs['username']
        followers = get_list_or_404(Follower, following__username=username)
        return followers
    serializer_class = FollowerSerializer


class FriendAPIView(generics.ListAPIView):
    """ [GET] Get The FriendList For A Spec-username """
    def get_queryset(self):
        username = self.kwargs['username']
        friends = Friend.objects.filter(Q(user1__username=username) | Q(user2__username=username))
        return friends
    serializer_class = FriendSerializer

