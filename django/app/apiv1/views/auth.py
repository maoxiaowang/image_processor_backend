from django.conf import settings
from django.forms import model_to_dict
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as DRFTokenObtainPairView, TokenRefreshView as DRFTokenRefreshView
)


def _token_cookie_kwargs():
    return {
        'expires': settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        'secure': settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        'httponly': settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        'samesite': settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        'domain': settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
        'path': settings.SIMPLE_JWT["AUTH_COOKIE_PATH"]
    }


class TokenObtainPairView(DRFTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        data['user'] = model_to_dict(
            instance=serializer.user,
            fields=['id', 'username']
        )
        response = Response(data, status=http_status.HTTP_200_OK)
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_ACCESS'],
            data['access'],
            **_token_cookie_kwargs()
        )
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            data['refresh'],
            **_token_cookie_kwargs()
        )
        return response


class TokenRefreshView(DRFTokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if 'access' in response.data:
            access_token = response.data['access']
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                **_token_cookie_kwargs()
            )
        return response


class TokenDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request):
        response = Response(status=http_status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_ACCESS'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        response.delete_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        return response


class WhoAmI(APIView):
    permission_classes = []

    @staticmethod
    def get(request):
        data = {
            'id': request.user.id,
            'username': request.user.username
        }
        return Response(data)
