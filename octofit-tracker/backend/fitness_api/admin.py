from django.contrib import admin

from .models import ActivityLog, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('display_name', 'user', 'team_name', 'weekly_goal_minutes')
	search_fields = ('display_name', 'user__username', 'team_name')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
	list_display = ('user', 'activity_type', 'duration_minutes', 'activity_date')
	list_filter = ('activity_type', 'activity_date')
	search_fields = ('user__username', 'notes')
