from django.conf import settings
from django.db import models


class Profile(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='profile',
	)
	display_name = models.CharField(max_length=100)
	bio = models.TextField(blank=True)
	weekly_goal_minutes = models.PositiveIntegerField(default=150)
	team_name = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['display_name']

	def __str__(self):
		return self.display_name


class ActivityLog(models.Model):
	RUN = 'run'
	WALK = 'walk'
	CYCLE = 'cycle'
	STRENGTH = 'strength'
	YOGA = 'yoga'

	ACTIVITY_CHOICES = [
		(RUN, 'Run'),
		(WALK, 'Walk'),
		(CYCLE, 'Cycle'),
		(STRENGTH, 'Strength'),
		(YOGA, 'Yoga'),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='activity_logs',
	)
	activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
	duration_minutes = models.PositiveIntegerField()
	calories_burned = models.PositiveIntegerField(null=True, blank=True)
	activity_date = models.DateField()
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-activity_date', '-created_at']

	def __str__(self):
		return f"{self.user} - {self.activity_type}"
