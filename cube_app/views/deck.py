from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cube_app.constants import USER_DECK_LIMIT

from ..models import Deck, DeckCard, DeckChange, DeckDashboard, DeckFavorite
from ..models import DeckView as DeckViewModel
from ..models import ScryfallCard
from ..serializers import (DeckChangeSerializer, DeckDashboardSerializer,
                           DeckFavoriteSerializer, DeckSerializer,
                           DeckViewSerializer, ScryfallCardSerializer)
from .deck_update_functions import updateDeckCards

# TODO verify request data with forms

class DecksView(APIView):
    """

    """
    def get(self, request):
        search = request.query_params.get('search', None)
        deckFormat = request.query_params.get('deckFormat', None)
        cardNames = request.query_params.getlist('cardNames[]', None)

        sort = request.query_params.get('sort', None)

        query = Q(private=False)

        if search:
            query.add(Q(name__icontains=search), Q.AND)

        if deckFormat:
            query.add(Q(format=deckFormat), Q.AND)

        if len(cardNames) > 0:
            query.add(Q(deckcard__name__in=cardNames), Q.AND)

        sortType = sort[1:] if sort[0] == '-' else sort
        sortReverse = True if sort[0] == '-' else False


        decks = DeckSerializer(Deck.objects.filter(query).annotate(favorites=Count('deckfavorite'), views=Count('deckview')), many=True).data
        decks.sort(key=lambda x: x[sortType if sortType else 'created'], reverse=sortReverse)

        return Response(decks)


    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user

        deckCount = Deck.objects.filter(user=user).count()
        if deckCount >= USER_DECK_LIMIT:
            return Response({"message": "User deck count at maximum allowed."}, status=status.HTTP_403_FORBIDDEN)

        deck = Deck(name="New Deck", user=user, description="", colors="", featuredArtUrl="", format="")
        deck.save()
                    
        return Response({"message": "Deck added!", "deckId": deck.id}, status=status.HTTP_201_CREATED)
    

class DeckView(APIView):
    """

    """
    def get(self, request, deckId=None):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        if deckId:
            decks = Deck.objects.filter(id=deckId)

            deck = DeckSerializer(decks, many=True)

            if len(deck.data) == 0:
                return Response({"message": "Deck not found!"}, status=status.HTTP_404_NOT_FOUND)
            
            dashboard = DeckDashboardSerializer(DeckDashboard.objects.filter(deck_id=deckId), many=True).data

            favorites = DeckFavoriteSerializer(DeckFavorite.objects.filter(deck_id=deckId), many=True).data
            views = DeckViewSerializer(DeckViewModel.objects.filter(deck_id=deckId), many=True).data

            deckCards = DeckCard.objects.filter(deck_id=deckId)
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
                "deck": deck.data[0],
                "main": ScryfallCardSerializer(mainBoard, many=True).data,
                "side": ScryfallCardSerializer(sideBoard, many=True).data,
                "maybe": ScryfallCardSerializer(maybeBoard, many=True).data,
                "acquire": ScryfallCardSerializer(acquireBoard, many=True).data,
                "dashboard": len(dashboard) > 0 and dashboard[0] or [],
                "favorites": len(favorites) or 0,
                "views": len(views) or 0
            }

            return Response(deck_with_cards)


    permission_classes = [IsAuthenticated]
    def patch(self, request, deckId):
        user = request.user

        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deck = Deck.objects.get(id=deckId, user_id=user.id)

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

        if 'dashboard' in request.data:
            savedDashboard = DeckDashboard.objects.filter(deck_id=deckId)

            if len(savedDashboard) > 0:
                savedDashboard[0].sections = request.data['dashboard']
                savedDashboard[0].save()
            else:
                dashboard = DeckDashboard(deck=deck, sections=request.data['dashboard'])
                dashboard.save()

        if 'commanderId' in request.data:
            deck.commander = ScryfallCard.objects.get(scryfallId=request.data['commanderId'])

        deck.save()

        updateDeckCards(request, deck)

        return Response({"message": "Deck updated!"}, status=status.HTTP_200_OK)
    
class UserDeckView(APIView):
    """

    """
    def get(self, request, userId):
        includePrivate = True if request.query_params.get('includePrivate', False) else False

        if userId:
            query = Q(user_id=userId)

            if includePrivate:
                query.add(Q(private=True) | Q(private=False), Q.AND)

            decks = Deck.objects.filter(query)
            return Response(DeckSerializer(decks, many=True).data)

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
    
class DeckFavoriteView(APIView):
    """

    """
    def get(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckFavorite = DeckFavorite.objects.filter(deck_id=deckId, user_id=request.user.id)

        if len(deckFavorite) > 0:
            return Response({"favorited": True})
        else:
            return Response({"favorited": False})

    def post(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckFavorite = DeckFavorite.objects.filter(deck_id=deckId, user_id=request.user.id)

        if len(deckFavorite) > 0:
            return Response({"message": "Deck already favorited!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            deckFavorite = DeckFavorite(deck_id=deckId, user_id=request.user.id)
            deckFavorite.save()

            return Response({"favorited": True}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckFavorite = DeckFavorite.objects.filter(deck_id=deckId, user_id=request.user.id)

        if len(deckFavorite) > 0:
            deckFavorite[0].delete()
            return Response({"favorited": False})
        else:
            return Response({"message": "Deck not favorited!"}, status=status.HTTP_404_NOT_FOUND)
        
class DeckViewsView(APIView):
    """

    """
    def get(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckViews = DeckViewModel.objects.filter(deck_id=deckId, user_id=request.user.id)

        if len(deckViews) > 0:
            return Response({"viewed": True})
        else:
            return Response({"viewed": False})

    def post(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckViews = DeckViewModel.objects.filter(deck_id=deckId, user_id=request.user.id)

        if len(deckViews) == 0:
            deckView = DeckViewModel(deck_id=deckId, user_id=request.user.id)
            deckView.save()

        return Response({"viewed": True}, status=status.HTTP_201_CREATED)