"""
polls/admin.py

Django Admin Configuration for Online Voting System

This file defines how the Poll, Option, and Vote
models appear and behave in the Django Admin interface.

Features:
- PollAdmin: Inline options, Active/Expired status, read-only fields
- OptionAdmin: Vote count display
- VoteAdmin: Read-only view of all votes
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Poll, Option, Vote


# ================================================
# Inline Admin: Allows adding Options directly inside Poll page
# ================================================
class OptionInline(admin.TabularInline):
    """
    Inline editor for Poll options.
    Allows editing options directly on the Poll admin page.
    """
    model = Option
    extra = 2  # Number of blank option rows to display by default
    min_num = 2  # Require at least 2 options (project requirement)
    show_change_link = True  # Adds a link to open the option editing page
    fields = ['text', 'vote_count_display']
    readonly_fields = ['vote_count_display']

    def vote_count_display(self, obj):
        """Display vote count for each option."""
        if obj.id:
            return obj.vote_count()
        return 0
    vote_count_display.short_description = 'Votes'


# ================================================
# Custom List Filter for Active/Expired Polls
# ================================================
class ActivePollFilter(admin.SimpleListFilter):
    """
    Adds a right-sidebar filter to show Active or Expired polls.
    Checks both is_active field and expires_at date.
    """
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'active':
            # Active and not expired
            return queryset.filter(is_active=True, expires_at__gt=now)
        elif self.value() == 'expired':
            # Expired (regardless of is_active field)
            return queryset.filter(expires_at__lte=now)
        elif self.value() == 'inactive':
            # Manually set as inactive
            return queryset.filter(is_active=False)
        return queryset


# ================================================
# Poll Admin Configuration
# ================================================
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Polls.
    Features:
    - Displays title, creator, dates, status, and total votes
    - Inline editing of Options
    - Sidebar filters for status and dates
    - Read-only fields for expired polls
    """
    list_display = [
        'title',
        'created_by',
        'created_at',
        'expires_at',
        'status_badge',
        'total_votes_display'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    list_filter = ['is_active', 'created_at', 'expires_at', ActivePollFilter]
    inlines = [OptionInline]
    readonly_fields = ['created_at', 'total_votes_display']
    
    fieldsets = (
        ('Poll Information', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Settings', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Statistics', {
            'fields': ('created_at', 'total_votes_display'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """
        Returns a colored badge showing poll status.
        Considers both is_active field and expiry date.
        """
        if not obj.is_active:
            return format_html(
                '<span style="background-color:#6c757d; color:white; padding:3px 8px; border-radius:4px;">Inactive</span>'
            )
        elif obj.is_expired():
            return format_html(
                '<span style="background-color:#dc3545; color:white; padding:3px 8px; border-radius:4px;">Expired</span>'
            )
        else:
            return format_html(
                '<span style="background-color:#28a745; color:white; padding:3px 8px; border-radius:4px;">Active</span>'
            )
    status_badge.short_description = "Status"

    def total_votes_display(self, obj):
        """Display total votes for the poll."""
        if obj.id:
            return obj.total_votes()
        return 0
    total_votes_display.short_description = 'Total Votes'

    def save_model(self, request, obj, form, change):
        """Set created_by to current user if creating new poll."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Make polls read-only if expired."""
        readonly = list(self.readonly_fields)
        if obj and obj.is_expired():
            # Make all fields readonly for expired polls
            return [field.name for field in self.model._meta.fields if field.name != 'is_active']
        return readonly


# ================================================
# Option Admin Configuration
# ================================================
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """
    Admin interface for poll options.
    Features:
    - Displays option text, associated poll, vote count
    - Sidebar filter by poll
    - Searchable by option text
    """
    list_display = ['text', 'poll', 'vote_count_badge', 'created_at']
    list_filter = ['poll', 'created_at']
    search_fields = ['text', 'poll__title']
    readonly_fields = ['created_at', 'vote_count_display']

    def vote_count_badge(self, obj):
        """
        Shows votes as a colored badge:
        - Green if votes > 0
        - Gray if votes == 0
        """
        votes = obj.vote_count()
        color = "#28a745" if votes > 0 else "#6c757d"
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; border-radius:4px;">{}</span>',
            color,
            votes
        )
    vote_count_badge.short_description = "Votes"

    def vote_count_display(self, obj):
        """Plain text vote count for detail view."""
        if obj.id:
            return obj.vote_count()
        return 0
    vote_count_display.short_description = 'Vote Count'


# ================================================
# Vote Admin Configuration
# ================================================
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Admin interface for votes.
    Features:
    - Displays user, poll, option, and timestamp
    - Sidebar filter by poll and option
    - Searchable by username or option text
    - All fields are read-only to preserve voting integrity
    """
    list_display = ['user', 'poll', 'option', 'voted_at']
    list_filter = ['poll', 'voted_at']
    search_fields = ['user__username', 'poll__title', 'option__text']
    readonly_fields = ['user', 'poll', 'option', 'voted_at']
    
    def has_add_permission(self, request):
        """Prevent manual vote creation in admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing votes."""
        return False