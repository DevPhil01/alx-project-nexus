"""
polls/serializers.py

Serializers for Poll, Option, and Vote models.
Handles validation and nested creation.
"""

from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from .models import Poll, Option, Vote


# ============================================================
# Option Serializer
# ============================================================
class OptionSerializer(serializers.ModelSerializer):
    """
    Serializer for poll options.
    Used when listing poll details or returning poll results.
    Includes vote count but makes it read-only.
    """
    vote_count = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.IntegerField)
    def get_vote_count(self, obj):
        """Get vote count for this option."""
        return obj.vote_count()

    class Meta:
        model = Option
        fields = ['id', 'text', 'vote_count']
        read_only_fields = ['id']


# ============================================================
# Poll Serializer (For Displaying Poll Details)
# ============================================================
class PollSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving polls.
    Includes all options nested inside with vote counts.
    """
    options = OptionSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField(read_only=True)
    
    @extend_schema_field(serializers.IntegerField)
    def get_total_votes(self, obj):
        """Get total votes for the poll."""
        return obj.total_votes()
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_expired(self, obj):
        """Check if poll has expired."""
        return obj.is_expired()

    class Meta:
        model = Poll
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'expires_at',
            'is_active',
            'is_expired',
            'created_by',
            'total_votes',
            'options',
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


# ============================================================
# Poll Creation Serializer (Admin or API Input)
# ============================================================
class PollCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used when creating a poll through the API.
    Allows sending options as a list of strings.
    
    Example:
    {
        "title": "Best Programming Language?",
        "description": "Vote for your favorite",
        "expires_at": "2025-12-31T23:59:59Z",
        "options": ["Python", "JavaScript", "Go"]
    }
    """
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        min_length=2
    )

    class Meta:
        model = Poll
        fields = ['title', 'description', 'expires_at', 'options']

    def validate_options(self, value):
        """Ensure at least 2 unique options."""
        if len(value) < 2:
            raise serializers.ValidationError(
                "A poll must have at least 2 options."
            )
        
        # Check for duplicates
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Options must be unique."
            )
        
        return value

    def validate_expires_at(self, value):
        """Ensure expiry date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiry date must be in the future."
            )
        return value

    def create(self, validated_data):
        """
        Custom create method:
        1. Create the poll with the authenticated user
        2. Create associated options
        """
        options_data = validated_data.pop('options')
        
        # Create the poll and set created_by to current user
        poll = Poll.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create all options belonging to the poll
        for text in options_data:
            Option.objects.create(poll=poll, text=text)
        
        return poll


# ============================================================
# Vote Serializer (For Casting Votes)
# ============================================================
class VoteSerializer(serializers.ModelSerializer):
    """
    Serializer for casting a vote.
    Validates that:
    - Poll is active and not expired
    - User has NOT voted before
    - Option belongs to the poll
    """

    class Meta:
        model = Vote
        fields = ['poll', 'option']

    def validate(self, data):
        """
        Comprehensive validation for voting.
        """
        poll = data['poll']
        option = data['option']
        user = self.context['request'].user

        # Check that the poll is active
        if not poll.is_active:
            raise serializers.ValidationError(
                "This poll is no longer active."
            )

        # Check if poll has expired
        if poll.is_expired():
            raise serializers.ValidationError(
                "This poll has expired."
            )

        # Ensure user has not already voted in this poll
        if Vote.objects.filter(user=user, poll=poll).exists():
            raise serializers.ValidationError(
                "You have already voted in this poll."
            )

        # Ensure option belongs to the correct poll
        if option.poll != poll:
            raise serializers.ValidationError(
                "Selected option does not belong to this poll."
            )

        return data

    def create(self, validated_data):
        """
        Create a new vote record associated with the logged-in user.
        """
        user = self.context['request'].user
        return Vote.objects.create(user=user, **validated_data)