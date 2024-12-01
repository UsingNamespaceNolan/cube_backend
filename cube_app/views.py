import logging
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from cube_app.constants import USER_DECK_LIMIT

from .deck_update_functions import updateDeckCards
from .models import Deck, DeckCard, DeckChange, ScryfallCard
from .serializers import (DeckCardSerializer, DeckChangeSerializer,
                          DeckSerializer, NewUserSerializer,
                          ScryfallCardSerializer,
                          TokenObtainPairSerializerWithUser, UserSerializer)

logger = logging.getLogger('cube_app')

class ScryfallCardView(APIView):
    def post(self, request):
        print('Scryfall')
        
        if 'cards' not in request.data:
            return Response({"message": "Provide a list of cards!"}, status=status.HTTP_400_BAD_REQUEST)

        cards = request.data['cards']

        index = 0
        cardsToAdd = []
        for card in cards:
            print(index, 'Adding:', card['name'])
            index += 1
            cardsToAdd.append(
                ScryfallCard(
                    scryfallId=card.get('id'),
                    set=card.get('set'),
                    setName=card.get('set_name'),
                    collectorNumber=card.get('collector_number'), 
                    releasedAt=card.get('released_at'),
                    cardBackId=card.get('card_back_id'), 
                    artist=card.get('artist'),

                    name=card.get('name'), 
                    colors=card.get('colors'), 
                    colorIdentity=card.get('color_identity'),
                    manaCost=card.get('mana_cost'),
                    cmc=card.get('cmc'),
                    rarity=card.get('rarity'),
                    typeLine=card.get('type_line'),
                    power=card.get('power'),
                    toughness=card.get('toughness'),
                    loyalty=card.get('loyalty'),
                    defense=card.get('defense'),
                    producedMana=card.get('produced_mana'),
                    oracleText=card.get('oracle_text'),
                    flavorText=card.get('flavor_text'),
                    
                    borderColor=card.get('border_color'),
                    frame=card.get('frame'),
                    fullArt=card.get('full_art'),
                    promo=card.get('promo'),
                    finishes=card.get('finishes'),
                    foil=card.get('foil'),
                    nonfoil=card.get('nonfoil'),
                    lang=card.get('lang'),
                    
                    imageURIs=card.get('image_uris'),
                    faces=card.get('faces'),
                    prices=card.get('prices'),
                    priceUris=card.get('price_uris'),
                    legalities=card.get('legalities')
                )
            )

        print('Creating cards...')
        ScryfallCard.objects.bulk_create(cardsToAdd)
        print('Done!')

        return Response({"message": "Cards added!"}, status=status.HTTP_201_CREATED)

# TODO verify request data with forms
class DeckView(APIView):
    """

    """

    def get(self, request):
        user = request.user

        if 'userId' in request.query_params:
            userId = request.query_params['id']
            decks = Deck.objects.filter(user_id=userId)
        else:
            decks = Deck.objects.filter(user_id=user.id)

        decks_serialized = DeckSerializer(decks, many=True)
        return Response(decks_serialized.data)
    

    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user

        deckCount = Deck.objects.filter(user=user).count()
        if deckCount >= USER_DECK_LIMIT:
            return Response({"message": "User deck count at maximum allowed."}, status=status.HTTP_403_FORBIDDEN)

        deck = Deck(name="New Deck", user=user, description="", colors="", featuredArtUrl="", format="")

        Deck.objects.bulk_create([deck])
                    
        return Response({"message": "Deck added!"}, status=status.HTTP_201_CREATED)


    permission_classes = [IsAuthenticated]
    def patch(self, request):
        user = request.user

        if 'id' not in request.data:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deck_id = request.data['id']
        deck = Deck.objects.get(id=deck_id, user_id=user.id)

        if 'name' in request.data:
            deck.name = request.data['name']

        if 'description' in request.data:
            deck.description = request.data['description']

        if 'private' in request.data:
            deck.private = request.data['private']

        if 'featuredArtUrl' in request.data:
            deck.featuredArtUrl = request.data['featuredArtUrl']

        if 'format' in request.data:
            deck.format = request.data['format']

        if 'colors' in request.data:
            deck.colors = request.data['colors']

        deck.save()

        updateDeckCards(request, deck)

        return Response({"message": "Deck updated!"}, status=status.HTTP_200_OK)

class DeckViewPublic(APIView):
    def get(self, request):
        if 'id' not in request.query_params:
            decks = Deck.objects.filter(private=False)
            decks_serialized = DeckSerializer(decks, many=True)

            return Response(decks_serialized.data)

        if 'id' in request.query_params:
            deck_id = request.query_params['id']
            decks = Deck.objects.filter(id=deck_id)

            deck_serialized = DeckSerializer(decks, many=True)

            if len(deck_serialized.data) == 0:
                return Response({"message": "Deck not found!"}, status=status.HTTP_404_NOT_FOUND)
            
            deckCards = DeckCard.objects.filter(deck_id=deck_id)
            deckCardCountsMappedById = {card.scryfallId: card for card in deckCards}
            scryfallCards = ScryfallCard.objects.filter(scryfallId__in=deckCardCountsMappedById.keys())

            mainBoard = []
            sideBoard = []
            maybeBoard = []
            acquireBoard = []
            
            for card in scryfallCards:
                if deckCardCountsMappedById[card.scryfallId].board == 'main':
                    card.count = deckCardCountsMappedById[card.scryfallId].count
                    mainBoard.append(card)
                if deckCardCountsMappedById[card.scryfallId].board == 'side':
                    card.count = deckCardCountsMappedById[card.scryfallId].count
                    sideBoard.append(card)
                if deckCardCountsMappedById[card.scryfallId].board == 'maybe':
                    card.count = deckCardCountsMappedById[card.scryfallId].count
                    maybeBoard.append(card)
                if deckCardCountsMappedById[card.scryfallId].board == 'acquire':
                    card.count = deckCardCountsMappedById[card.scryfallId].count
                    acquireBoard.append(card)

            deck_with_cards = {
                "deck": deck_serialized.data[0],
                "main": ScryfallCardSerializer(mainBoard, many=True).data,
                "side": ScryfallCardSerializer(sideBoard, many=True).data,
                "maybe": ScryfallCardSerializer(maybeBoard, many=True).data,
                "acquire": ScryfallCardSerializer(acquireBoard, many=True).data
            }

            return Response(deck_with_cards)
        
class DeckChangeView(APIView):
    """

    """
    def get(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        mainBoardChanges = DeckChange.objects.filter(deck_id=deckId, board='main')
        sideBoardChanges = DeckChange.objects.filter(deck_id=deckId, board='side')
        maybeBoardChanges = DeckChange.objects.filter(deck_id=deckId, board='maybe')
        acquireBoardChanges = DeckChange.objects.filter(deck_id=deckId, board='acquire')

        deckChanges = {
            "main": DeckChangeSerializer(mainBoardChanges, many=True).data,
            "side": DeckChangeSerializer(sideBoardChanges, many=True).data,
            "maybe": DeckChangeSerializer(maybeBoardChanges, many=True).data,
            "acquire": DeckChangeSerializer(acquireBoardChanges, many=True).data
        }

        return Response(deckChanges)

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

