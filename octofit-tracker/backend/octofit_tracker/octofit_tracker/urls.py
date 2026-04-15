import os

from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from fitness_api.views import (
    ActivityLogViewSet,
    CurrentUserView,
    LoginView,
    LogoutView,
    ProfileViewSet,
    RegisterView,
)

codespace_name = os.environ.get('CODESPACE_NAME')
if codespace_name:
    base_url = f"https://{codespace_name}-8000.app.github.dev"
else:
    base_url = "http://localhost:8000"

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profile')
router.register('activities', ActivityLogViewSet, basename='activity')


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'OctoFit Tracker API',
        'base_url': base_url,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/', include(router.urls)),
]
