"""
polls/models.py

Database models for the Online Poll System.
Optimized for real-time result computation with proper indexing.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Poll(models.Model):
    """
    Represents a poll with title, creation date, and expiry.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Optional expiry
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='polls'
    )
    is_active = models.BooleanField(default=True)  # Manual active/inactive toggle

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return self.title

    def is_expired(self):
        """Check if poll has expired based on expires_at."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def total_votes(self):
        """Calculate total votes across all options."""
        return Vote.objects.filter(poll=self).count()


class Option(models.Model):
    """
    Represents a poll option/choice.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['poll']),
        ]

    def __str__(self):
        return f"{self.poll.title} - {self.text}"

    def vote_count(self):
        """
        Calculate votes for this option.
        Uses efficient count() query instead of denormalized field.
        """
        return self.votes.count()


class Vote(models.Model):
    """
    Represents a user's vote on a poll.
    Ensures one vote per user per poll via unique_together.
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure one vote per user per poll
        unique_together = ['user', 'poll']
        indexes = [
            models.Index(fields=['poll', 'user']),
            models.Index(fields=['option']),
            models.Index(fields=['voted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} voted for {self.option.text}"