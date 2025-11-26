"""
polls/auth_urls.py

URL routes for authentication endpoints.
"""

from django.urls import path
from .auth_views import (
    UserRegistrationView,
    UserProfileView,
    ChangePasswordView,
    UserListView
)

urlpatterns = [
    # User Registration
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    
    # User Profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    # Password Management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # User List (Admin only)
    path('users/', UserListView.as_view(), name='user-list'),
]