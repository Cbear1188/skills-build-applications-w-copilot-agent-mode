from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import ActivityLog, Profile

User = get_user_model()


class StringIdModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name in ('id', 'user'):
            if field_name in representation and representation[field_name] is not None:
                representation[field_name] = str(representation[field_name])
        return representation


class ProfileSerializer(StringIdModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'display_name',
            'bio',
            'weekly_goal_minutes',
            'team_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ActivityLogSerializer(StringIdModelSerializer):
    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'user',
            'activity_type',
            'duration_minutes',
            'calories_burned',
            'activity_date',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class UserSummarySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    display_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'display_name']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        display_name = validated_data.pop('display_name', '').strip()
        user = User.objects.create_user(**validated_data)
        profile = user.profile
        profile.display_name = display_name or user.username
        profile.save(update_fields=['display_name', 'updated_at'])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs.get('username'),
            password=attrs.get('password'),
        )
        if user is None:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials.']})
        attrs['user'] = user
        return attrs


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    user = UserSummarySerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)

    @staticmethod
    def build_response(user):
        token, _ = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'user': UserSummarySerializer(user).data,
            'profile': ProfileSerializer(user.profile).data,
        }