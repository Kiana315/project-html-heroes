from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



app_name = "SocialDistribution"

""" May edit this part to have new web pages"""
urlpatterns = [
    path("", views.IndexView, name="index"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('signup/', views.signup_view, name='signup'),
] 

