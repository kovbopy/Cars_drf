from django.db.models import Count, Case, When
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from users.permissions import UserPermission
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

