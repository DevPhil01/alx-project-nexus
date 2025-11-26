"""
Views for the Online Voting System.

This file contains all API logic for:
1. Listing active polls
2. Retrieving a single poll with its options
3. Creating a poll with options
4. Casting a vote
5. Viewing poll results in real-time

All views use Django REST Framework (DRF).
Includes Redis caching and rate limiting for performance and security.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit

from .models import Poll, Vote
from .serializers import (
    PollSerializer,
    PollCreateSerializer,
    VoteSerializer
)


# =====================================================================
# 1. LIST ALL ACTIVE POLLS & CREATE NEW POLLS
# =====================================================================

class PollListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/polls/  → List all ACTIVE polls (cached for 5 minutes)
    POST /api/polls/  → Create a new poll (ADMIN ONLY)
    
    Rate limited: 100 requests per hour for list, 10 requests per hour for create

    Returns a list of all active polls with their options and vote counts.
    Only active (non-expired) polls are shown.
    
    For creating polls:
    Example Request:
    {
        "title": "Best Programming Language?",
        "description": "Vote for your favorite",
        "expires_at": "2025-12-31T23:59:59Z",
        "options": ["Python", "Go", "JavaScript"]
    }
    """
    
    def get_permissions(self):
        """
        Different permissions for different methods:
        - GET: Anyone can view (IsAuthenticatedOrReadOnly)
        - POST: Only admins can create (IsAdminUser)
        """
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        """Use different serializers for list vs create."""
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollSerializer
    
    def get_queryset(self):
        """
        Retrieve polls that are still active.
        Optimized with prefetch_related to avoid N+1 queries.
        """
        return Poll.objects.filter(
            is_active=True
        ).prefetch_related('options').order_by('-created_at')
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @method_decorator(ratelimit(key='ip', rate='100/h', method='GET'))
    def get(self, request, *args, **kwargs):
        """List polls with caching and rate limiting."""
        return super().get(request, *args, **kwargs)
    
    @method_decorator(ratelimit(key='user', rate='10/h', method='POST'))
    def post(self, request, *args, **kwargs):
        """Create poll with rate limiting (admin only)."""
        return super().post(request, *args, **kwargs)


# =====================================================================
# 2. RETRIEVE A SINGLE POLL
# =====================================================================

class PollDetailView(generics.RetrieveAPIView):
    """
    GET /api/polls/<id>/

    Retrieve the full details of a poll including its options
    and real-time vote counts.
    
    Cached for 2 minutes, rate limited to 60 requests per hour per IP.
    """
    queryset = Poll.objects.prefetch_related('options').all()
    serializer_class = PollSerializer
    
    @method_decorator(cache_page(60 * 2))  # Cache for 2 minutes
    @method_decorator(ratelimit(key='ip', rate='60/h', method='GET'))
    def get(self, request, *args, **kwargs):
        """Retrieve poll with caching and rate limiting."""
        return super().get(request, *args, **kwargs)


# =====================================================================
# 3. CAST A VOTE
# =====================================================================

class VoteCreateView(generics.CreateAPIView):
    """
    POST /api/polls/<poll_id>/vote/

    Allows an authenticated user to cast a vote on a poll.
    
    Rate limited: 20 votes per hour per user to prevent spam.

    Example Request:
    {
        "poll": 1,
        "option": 3
    }

    The VoteSerializer automatically:
    - Ensures the poll is active and not expired
    - Ensures the user has not voted before
    - Ensures the option belongs to the selected poll
    """
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]
    
    @method_decorator(ratelimit(key='user', rate='20/h', method='POST'))
    def post(self, request, *args, **kwargs):
        """Create vote with rate limiting and cache invalidation."""
        response = super().post(request, *args, **kwargs)
        
        # Invalidate cache for poll results when a vote is cast
        if response.status_code == status.HTTP_201_CREATED:
            poll_id = request.data.get('poll')
            cache.delete(f'poll_results_{poll_id}')
        
        return response


# =====================================================================
# 4. POLL RESULTS (REAL-TIME)
# =====================================================================

class PollResultView(APIView):
    """
    GET /api/polls/<poll_id>/results/

    Returns real-time results for a poll including:
    - poll title
    - total votes
    - each option with its vote count

    Example Response:
    {
        "poll": "Favourite Fruit",
        "total_votes": 124,
        "results": [
            {"option": "Mango", "votes": 80},
            {"option": "Banana", "votes": 30},
            {"option": "Apple", "votes": 14}
        ]
    }
    
    Results cached for 1 minute. Rate limited to 100 requests per hour.
    Accessible to all users (no authentication required).
    """
    permission_classes = []  # Public endpoint

    @method_decorator(ratelimit(key='ip', rate='100/h', method='GET'))
    def get(self, request, poll_id):
        # Try to get results from cache first
        cache_key = f'poll_results_{poll_id}'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return Response(cached_results, status=status.HTTP_200_OK)
        
        # If not in cache, fetch from database
        try:
            poll = Poll.objects.prefetch_related('options').get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Collect option results using the model method
        options = poll.options.all()
        results_data = [
            {"option": option.text, "votes": option.vote_count()}
            for option in options
        ]

        # Summary data
        data = {
            "poll": poll.title,
            "total_votes": poll.total_votes(),
            "results": results_data
        }
        
        # Cache results for 1 minute (60 seconds)
        cache.set(cache_key, data, 60)

        return Response(data, status=status.HTTP_200_OK)


# =====================================================================
# RATE LIMIT ERROR HANDLER
# =====================================================================

def rate_limited_error(request, exception):
    """
    Custom view for rate limit errors.
    Returns a JSON response instead of HTML.
    """
    return Response(
        {
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please try again later."
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS
    )