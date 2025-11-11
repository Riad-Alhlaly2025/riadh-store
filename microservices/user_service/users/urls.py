"""
URLs for the user service.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('register/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('login/', views.LoginView.as_view(), name='user_login'),
]