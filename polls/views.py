"""
Views for the Online Voting System.

This file contains all API logic for:
1. Listing active polls
2. Retrieving a single poll with its options
3. Creating a poll with options
4. Casting a vote
5. Viewing poll results in real-time

All views use Django REST Framework (DRF).
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView

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
    GET  /api/polls/  → List all ACTIVE polls
    POST /api/polls/  → Create a new poll (authenticated users only)

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
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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


# =====================================================================
# 2. RETRIEVE A SINGLE POLL
# =====================================================================

class PollDetailView(generics.RetrieveAPIView):
    """
    GET /api/polls/<id>/

    Retrieve the full details of a poll including its options
    and real-time vote counts.
    """
    queryset = Poll.objects.prefetch_related('options').all()
    serializer_class = PollSerializer


# =====================================================================
# 3. CAST A VOTE
# =====================================================================

class VoteCreateView(generics.CreateAPIView):
    """
    POST /api/polls/<poll_id>/vote/

    Allows an authenticated user to cast a vote on a poll.

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
    
    Accessible to all users (no authentication required).
    """
    permission_classes = []  # Public endpoint

    def get(self, request, poll_id):
        # Attempt to retrieve requested poll
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

        return Response(data, status=status.HTTP_200_OK)