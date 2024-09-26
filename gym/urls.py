# gym/urls.py
from django.urls import path
from .views import GymOwnerRegisterView, GymOwnerLoginView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, PlanViewSet, MembershipViewSet,GymOwnerProfileView,CustomTokenRefreshView



router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'memberships', MembershipViewSet, basename='membership')


urlpatterns = [
    path('register/', GymOwnerRegisterView.as_view(), name='register'),
    path('login/', GymOwnerLoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('gym-profile/', GymOwnerProfileView.as_view(), name='gym_owner_profile'),
    path('', include(router.urls)),
]

