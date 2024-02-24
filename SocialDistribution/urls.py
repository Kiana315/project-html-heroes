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
    # Basic PAGE View Settings:
    path("", IndexView.as_view(), name="PAGE_Home"),
    path('admin/', admin.site.urls, name="PAGE_Admin"),
    path("login/", LoginView.as_view(), name="PAGE_Login"),
    path('logout/', LogoutView.as_view(), name='PAGE_Logout'),
    path("signup/", signupView, name="PAGE_Signup"),
    path("friendPosts/<str:username>/", FriendPostsView.as_view(), name="PAGE_FriendPosts"),
    path("inbox/<str:username>/", InboxView.as_view(), name="PAGE_Inbox"),
    path("posts/<int:post_id>/", PostDetailView.as_view(), name="PAGE_postDetail"),

    # Identity API System:
    path("api/user/<str:username>/", UserAPIView.as_view(), name="API_USER"),
    # GET Self User/Profile Info        --> Test Success
    path("api/user/<str:user1_id>/<str:user2_id>/", UserAPIView.as_view(), name="API_USER_TWO"),
    # GET Other's User/Profile Info     --> Test Success
    path("profile/<str:username>/", profileView, name="PAGE_Profile"),
    path("profile/<str:selfUsername>/<str:targetUsername>/", otherProfileView, name="PAGE_OtherProfile"),
    path("profile/<str:username>/upload-avatar/", upload_avatar, name="API_UploadAvatar"),
    path("profile/<str:username>/update-bio/", update_bio, name="API_UpdateBio"),
    path("profile/<str:username>/update-username/", update_username, name="API_UpdateUsername"),
    path("profile/<str:username>/draft/", author_draft_view, name="author-draft"),

    # Friend API System:
    path('search/', views.search_user, name='PAGE_SearchUser'),
    path('profile/<str:username>/followers/', FollowerView.as_view(), name='PAGE_FollowersList'),
    path('profile/<str:username>/following/', FollowingView.as_view(), name='PAGE_FollowingList'),
    path('profile/<str:username>/friends/', FriendView.as_view(), name='PAGE_FriendList'),

    path("api/user/<str:username>/followers/", FollowersAPIView.as_view(), name="API_GETFollowers"),        # GET User FollowerList     --> Test Success
    path("api/user/<str:username>/following/", FollowingAPIView.as_view(), name="API_GETFollowing"),        # GET User FollowerList     --> Test Success
    path("api/user/<str:username>/friends/", FriendsAPIView.as_view(), name="API_GETFriends"),              # GET User FriendList       --> Test Success

    path('api/user/<str:selfUsername>/followerOf/<str:targetUsername>/', CreateFollowerAPIView.as_view(), name='API_POSTFollowerOf'),       # POST Create FollowerOf Case     --> Test Success
    path('api/user/<str:selfUsername>/following/<str:targetUsername>/', CreateFollowingAPIView.as_view(), name='API_POSTFollowing'),        # POST Create Following Case
    path('api/user/<str:selfUsername>/friend/<str:targetUsername>/', createFriendshipAPIView, name='API_POSTFriend'),                       # POST Create Friend Case

    # Post API System:
    path("api/pps/", PPsAPIView.as_view(), name="API_PPs"),                                                     # GET PublicPostsList       --> Test Success
    path("api/fps/<str:username>/", FPsAPIView.as_view(), name="API_FPs"),                                      # GET FriendPostsList       --> Test Success
    path("api/nps/", NPsAPIView.as_view(), name="API_NPs"),                                                     # POST NewPosts             --> Test Success
    path('api/posts/<int:post_id>/', PostOperationAPIView.as_view(), name='API_PDetail'),                       # GET/PUT/DELETE PostsOperations
    path("api/posts/<int:post_id>/comments/", CommentAPIView.as_view(), name='API_PComms'),                     # GET/POST CommentList/NewComment  --> Test Success
    path("api/posts/<int:post_id>/likes/", LikeAPIView.as_view(), name='API_PLikes'),                           # GET/POST LikeList/NewLike        --> Test Success


    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:post_id>/update/', update_post, name='update_post'),


    # Inbox API System:
    path("api/msgs/<str:username>/", MsgsAPIView.as_view(), name="API_MSGs"),                                   # GET InboxMessages         --> ?



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
