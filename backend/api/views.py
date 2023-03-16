from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import CustomAuthTokenSerializer


class CustomAuthToken(ObtainAuthToken):
    """Авторизация пользователя."""
    serializer_class = CustomAuthTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'token': str(token)},
            status=status.HTTP_201_CREATED
        )
