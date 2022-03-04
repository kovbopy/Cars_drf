from django.urls import path, include
from rest_framework import routers
from .views import CarViewSet, CarUserViewSet

router = routers.SimpleRouter()
router.register('cars', CarViewSet, basename='car')
router.register('user_car', CarUserViewSet, basename='user_Car')


urlpatterns = [
    path('', include(router.urls)),
]