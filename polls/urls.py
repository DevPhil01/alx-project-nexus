"""
polls/urls.py

This file contains all URL routes for the Polls API.
Each route calls a View that handles poll creation,
voting, listing, retrieving details, and viewing poll results.
"""

from django.urls import path
from . import views
from .views import ApiIndexView


urlpatterns = [
    path("", ApiIndexView.as_view(), name="api-index"),
    
    # ===========================
    # POLL ROUTES
    # ===========================
    # GET  /api/polls/     → List all polls
    # POST /api/polls/     → Create a new poll with options
    path(
        "polls/",
        views.PollListCreateView.as_view(),
        name="poll-list-create"
    ),

    # GET /api/polls/<id>/ → Retrieve poll details
    path(
        "polls/<int:pk>/",
        views.PollDetailView.as_view(),
        name="poll-detail"
    ),

    # ===========================
    # VOTE ROUTE
    # ===========================
    # POST /api/polls/<poll_id>/vote/
    #     → Cast a vote on a poll
    #     → Requires: { "poll": <poll_id>, "option": <option_id> }
    path(
        "polls/<int:poll_id>/vote/",
        views.VoteCreateView.as_view(),
        name="poll-vote"
    ),

    # ===========================
    # RESULTS ROUTE
    # ===========================
    # GET /api/polls/<poll_id>/results/
    #     → Returns real-time vote counts for each option
    path(
        "polls/<int:poll_id>/results/",
        views.PollResultView.as_view(),
        name="poll-results"
    ),
]
