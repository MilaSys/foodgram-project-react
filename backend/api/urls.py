from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomAuthToken

app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    path(
        'auth/token/login/',
        CustomAuthToken.as_view(),
        name='login',
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
