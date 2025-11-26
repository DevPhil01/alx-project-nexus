"""
online_poll_system/urls.py

This file contains project-level URL routes.
It includes:
- Admin panel
- JWT Authentication endpoints
- Polls API routes (from polls/urls.py)
- Swagger/OpenAPI documentation
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ===========================
    # Admin Panel
    # ===========================
    path("admin/", admin.site.urls),

    # ===========================
    # JWT Authentication
    # ===========================
    path("api/token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),

    # ===========================
    # User Authentication & Registration
    # ===========================
    path("api/auth/", include("polls.auth_urls")),

    # ===========================
    # Polls API Routes
    # All routes from polls/urls.py will be under /api/
    # ===========================
    path("api/", include("polls.urls")),

    # ===========================
    # API Documentation
    # ===========================
    # OpenAPI Schema (JSON/YAML)
    path("api/schema/", SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI (Interactive API documentation)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    
    # ReDoc UI (Alternative documentation view)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]