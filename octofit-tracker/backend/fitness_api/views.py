from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActivityLog, Profile
from .serializers import (
    ActivityLogSerializer,
    AuthResponseSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
	serializer_class = ProfileSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Profile.objects.select_related('user').filter(user=self.request.user)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class ActivityLogViewSet(viewsets.ModelViewSet):
	serializer_class = ActivityLogSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return ActivityLog.objects.select_related('user').filter(user=self.request.user)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class RegisterView(APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = RegistrationSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response(
			AuthResponseSerializer.build_response(user),
			status=status.HTTP_201_CREATED,
		)


class LoginView(ObtainAuthToken):
	permission_classes = [permissions.AllowAny]
	serializer_class = LoginSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		return Response(AuthResponseSerializer.build_response(serializer.validated_data['user']))


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		Token.objects.filter(user=request.user).delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		return Response(AuthResponseSerializer.build_response(request.user))
