from django.urls import path
from .views import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from . import views

app_name = "SocialDistribution"

router = DefaultRouter()
router.register(r'posts', NPsAPIView)

urlpatterns = [
    # Page View Addresses
    path("", IndexView.as_view(), name="home"),
    path('admin/', admin.site.urls, name="admin"),
    path("login/", LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("signup/", signupView, name="signup"),
    path("friendPosts/<str:username>/", FriendPostsView.as_view(), name="friendPosts"),
    path("profile/<str:username>/", profileView, name="profile"),
    path("profile/<str:username>/upload-avatar/", upload_avatar, name="upload-avatar"),
    path("profile/<str:username>/update-bio/", update_bio, name="update-bio"),
    path("profile/<str:username>/update-username/", update_username, name="update-username"),
    path("inbox/<str:username>/", InboxView.as_view(), name="inbox"),
    # path("profile/<str:username>/followers", FollowersListView.as_view, name="followers"),
    # path("profile/<str:username>/following", FollowingListView.as_view, name="following"),
    #path("posts/<str:username>", postView, name="post"),
    path("posts/<int:post_id>/", PostDetailView.as_view(), name="post_detail"),
    path('search/', views.search_user, name='search_user'),



    # API End-points Addresses
    path("api/pps/", PPsAPIView.as_view(), name="API_PPs"),                                         # GET PublicPostsList       --> Test Success
    path("api/fps/<str:username>/", FPsAPIView.as_view(), name="API_FPs"),                          # GET FriendPostsList       --> Test Success
    path("api/nps/", NPsAPIView.as_view(), name="API_NPs"),                                         # POST NewPosts             --> Test Success

    path("api/msgs/<str:username>/", MsgsAPIView.as_view(), name="API_MSGs"),                       # GET InboxMessages         --> ?
    path("api/user/<str:username>/", UserAPIView.as_view(), name="API_USER"),                       # GET User/Profile Info     --> Test Success
    path("api/user/<str:username>/followers/", FollowerAPIView.as_view(), name="API_USERFrd"),       # GET User FollowerList     --> Test Success
    path("api/user/<str:username>/friends/", FriendAPIView.as_view(), name="API_USERFow"),          # GET User FriendList       --> Test Success
    path('api/posts/<int:post_id>/', PostOperationAPIView.as_view(), name='API_PDetail'),                # GET/PUT/DELETE PostsOperations
    path("api/posts/<int:post_id>/comments/", CommentAPIView.as_view(), name='API_PComms'),              # GET/POST CommentList/NewComment  --> Test Success
    path("api/posts/<int:post_id>/likes/", LikeAPIView.as_view(), name='API_PLikes'),                    # GET/POST LikeList/NewLike        --> Test Success
    path('profile/<str:username>/followers/', FollowersListView.as_view(), name='followers-list'),
    path('profile/<str:username>/following/', FollowingListView.as_view(), name='following-list'),
    #path('profile/<str:username>/friends/', FriendsListView.as_view(), name='friends-list'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
