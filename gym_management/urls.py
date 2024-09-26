# gym_management/urls.py
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gym.urls')),  # Include gym app URLs
]
