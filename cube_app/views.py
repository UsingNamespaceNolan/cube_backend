from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import APIException
from django.http import HttpResponse, JsonResponse
import logging

from cube_app.constants import USER_DECK_LIMIT

from .models import Deck, DeckCard
from .serializers import NewUserSerializer, UserSerializer

logger = logging.getLogger('cube_app')

class DeckView(APIView):
    """

    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.save()

        user_deck_count = Deck.objects.filter(user=user).count()
        
        if user_deck_count >= USER_DECK_LIMIT:
            return Response({"message": "User deck count at maximum allowed."}, status=status.HTTP_403_FORBIDDEN)

        # first create the deck to get a primary key id
        user_deck = Deck(name=request.data['name'], user=user)
        user_deck.save()
        logger.info(f'deck {user_deck}')
        logger.info(f'id {user_deck.id}')
        logger.info(f'name {user_deck.name}')

        # then add all the cards in the deck with the new deck id
        cards_in_deck = [DeckCard(deck=user_deck, scryfall_id=card['id'], name=card['name']) for card in request.data['cards']]

        logger.info(cards_in_deck)
        DeckCard.objects.bulk_create(cards_in_deck)

        return Response({"message": "Deck added!"}, status=status.HTTP_201_CREATED)

class RegisterUserView(APIView):
    """
    API endpoint to register a new user.
    """
    authentication_classes = ([])
    permission_classes = [AllowAny]
    def post(self, request):
        newUserSerializer = NewUserSerializer(data=request.data)
        if newUserSerializer.is_valid():
            newUserSerializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(newUserSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """
    View to list all users in the system.

    * Requires JWT authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
    

class LoginView(APIView):
    """
    
    """
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        if username is None or password is None:
            raise APIException(f"Provide valid credentials!")
        user = authenticate(username=username, password=password)
        if user is not None:
            print(user)
            login(request, user)

            return HttpResponse({"You're logged in"})
        return JsonResponse(
            {"detail": "Invalid credentials"},
            status=400,
        )
    

class LogoutView(APIView):
    """
    
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # blacklist token?

        return JsonResponse({"response": "Logout success"})


@ensure_csrf_cookie
def set_csrf_token(request):
    """
    This will be `/api/set-csrf-cookie/` on `urls.py`
    """
    return JsonResponse({"details": "CSRF cookie set"})

