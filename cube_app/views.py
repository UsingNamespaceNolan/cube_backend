from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import APIException
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
import logging

from cube_app.constants import USER_DECK_LIMIT

from .models import Deck, DeckCard
from .serializers import DeckSerializer, NewUserSerializer, TokenObtainPairSerializerWithUser, UserSerializer

logger = logging.getLogger('cube_app')

# TODO verify request data with forms
class DeckView(APIView):
    """

    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        user_deck_count = Deck.objects.filter(user=user).count()
        if user_deck_count >= USER_DECK_LIMIT:
            return Response({"message": "User deck count at maximum allowed."}, status=status.HTTP_403_FORBIDDEN)

        cards_in_deck = []
        # first create the deck to get a primary key id
        user_deck = Deck(name=request.data['name'], user=user)

        try:
            user_deck.save()
        except IntegrityError:
            return Response({"message": "Deck name already exists!"}, status=status.HTTP_409_CONFLICT)

        # then add all the cards in the deck with the new deck id
        found_cards_scryfall_id = set()
        for card in request.data['cards']:
            if card['id'] not in found_cards_scryfall_id:
                cards_in_deck.append(DeckCard(deck=user_deck, scryfall_id=card['id'], name=card['name']))

        logger.info(cards_in_deck)
        DeckCard.objects.bulk_create(cards_in_deck)

        # then add sideboard and sideboard cards

        return Response({"message": "Deck added!"}, status=status.HTTP_201_CREATED)


    def get(self, request):
        user = request.user

        if 'name' in request.query_params:
            deck_name = request.query_params['name']
            decks = Deck.objects.filter(name=deck_name, user_id=user.id)
        else:
            decks = Deck.objects.filter(user_id=user.id)

        decks_serialized = DeckSerializer(decks, many=True)
        return Response(decks_serialized.data)

class RegisterUserView(APIView):
    """
    API endpoint to register a new user.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        newUserSerializer = NewUserSerializer(data=request.data)
        if newUserSerializer.is_valid():
            newUserSerializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(newUserSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Endpoint to query/update information about the current logged in user.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Returns the current logged in user
        """
        user_serialized = UserSerializer(request.user)
        return Response(user_serialized)
    

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
    

class TokenObtainPairWithUser(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerWithUser



@ensure_csrf_cookie
def set_csrf_token(request):
    """
    This will be `/api/set-csrf-cookie/` on `urls.py`
    """
    return JsonResponse({"details": "CSRF cookie set"})

