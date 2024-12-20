import logging

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import (NewUserSerializer,
                           TokenObtainPairSerializerWithUser, UserSerializer)

logger = logging.getLogger('cube_app')

class RegisterUserView(APIView):
    """
    API endpoint to register a new user.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        newUserSerializer = NewUserSerializer(data=request.data)

        if newUserSerializer.is_valid():
            newUserSerializer.save()
            return Response({ "message": "User registered successfully!" }, status=status.HTTP_201_CREATED)
        else:
            return Response(newUserSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Endpoint to query/update information about the current logged in user.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Returns the current logged in user
        """
        user_serialized = UserSerializer(request.user)
        return Response(user_serialized.data)
    

class LogoutView(APIView):
    """
    
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # blacklist token?

        return JsonResponse({"response": "Logout success"})
    

class TokenObtainPairWithUser(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerWithUser


@ensure_csrf_cookie
def set_csrf_token(request):
    """
    This will be `/api/set-csrf-cookie/` on `urls.py`
    """
    return JsonResponse({"details": "CSRF cookie set"})

