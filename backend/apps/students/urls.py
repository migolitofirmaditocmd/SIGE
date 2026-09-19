from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuardianViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
