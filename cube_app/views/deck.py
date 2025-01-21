from math import ceil
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cube_app.constants import USER_DECK_LIMIT

from ..models import Deck, DeckCard, DeckChange, DeckDashboard, DeckFavorite, Folder, DeckKitLink
from ..models import DeckView as DeckViewModel
from ..models import ScryfallCard
from ..serializers import (DeckChangeSerializer, DeckDashboardSerializer,
                           DeckFavoriteSerializer, DeckSerializer,
                           DeckViewSerializer, ScryfallCardSerializer)
from .deck_update_functions import updateDeckCardsFromRequest

# TODO verify request data with forms

class DecksView(APIView):
    """

    """
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        items = int(request.query_params.get('items', 50))

        search = request.query_params.get('search', None)
        deckFormat = request.query_params.get('deckFormat', None)
        sort = request.query_params.get('sort', None)
        commander = request.query_params.get('commander', None)
        partner = request.query_params.get('partner', None)

        cardNames = request.query_params.getlist('cardNames[]', None)
        board = request.query_params.get('board', None)
        exclusiveCardSearch = request.query_params.get('exclusiveCardSearch', None)

        onlyKits = True if request.query_params.get('onlyKits', False) == 'true' else False
        userDecks = True if request.query_params.get('userDecks', False) == 'true' else False
        excludeIds = request.query_params.getlist('excludeIds[]', [])
        includeIds = request.query_params.getlist('includeIds[]', [])

        query = Q(private=False)
        query.add(Q(inProgress=False), Q.AND)

        if search:
            query.add(Q(name__icontains=search), Q.AND)

        if deckFormat:
            query.add(Q(format=deckFormat), Q.AND)

        if commander:
            query.add(Q(commander__name=commander), Q.AND)

        if partner:
            query.add(Q(partner__name=partner), Q.AND)

        if userDecks:
            query.add(Q(user_id=request.user.id), Q.AND)

        if onlyKits:
            query.add(Q(isKit=True), Q.AND)
        else:
            query.add(Q(isKit=False), Q.AND)

        if len(cardNames) > 0:
            if not board:
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

            if board == 'main':
                query.add(Q(deckcard__board='main'), Q.AND)
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

            if board == 'side':
                query.add(Q(deckcard__board='side'), Q.AND)
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

            if board == 'maybe':
                query.add(Q(deckcard__board='maybe'), Q.AND)
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

            if board == 'acquire':
                query.add(Q(deckcard__board='acquire'), Q.AND)
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

        if includeIds:
            query.add(Q(id__in=includeIds), Q.AND)

        if exclusiveCardSearch:
            deckQuery = Deck.objects.filter(query).exclude(id__in=excludeIds)

            for card in cardNames:
                deckQuery = deckQuery.filter(deckcard__name=card)
            
            deckQuery = (
                deckQuery
                    .annotate(favorites=Count('deckfavorite'), views=Count('deckview'))
                    .order_by(sort if sort else 'created')
                    [(page-1)*items:page*items]
            )

            total = Deck.objects.filter(query).count()

            return Response({ 
                "meta": {
                    "page": page,
                    "items": items,

                    "totalItems": total,
                    "totalPages": ceil(total / items),
                }, 
                "data": DeckSerializer(deckQuery, many=True).data 
            })

        decks = (
            Deck.objects
                .filter(query)
                .exclude(id__in=excludeIds)
                .annotate(favorites=Count('deckfavorite'), views=Count('deckview'))
                .order_by(sort if sort else 'created')
                [(page-1)*items:page*items]
        )
        
        total = Deck.objects.filter(query).count()
        
        return Response({ 
            "meta": {
                "page": page,
                "items": items,

                "totalItems": total,
                "totalPages": ceil(total / items),
            }, 
            "data": DeckSerializer(decks, many=True).data
        })


    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user

        deckCount = Deck.objects.filter(user=user).count()
        if deckCount >= USER_DECK_LIMIT:
            return Response({"message": "User deck count at maximum allowed."}, status=status.HTTP_403_FORBIDDEN)

        deck = Deck(
            user=user, 
            name=request.data.get('name', "New Deck"),
            description=request.data.get('description', ""),
            private=request.data.get('private', True),
            colors=request.data.get('colors', ""),
            featuredArtUrl=request.data.get('featuredArtUrl', ""),
            format=request.data.get('format', ""),
        )
        
        if 'commanderId' in request.data:
            deck.commander = ScryfallCard.objects.get(scryfallId=request.data['commanderId'])

        deck.save()

        if 'dashboard' in request.data:
                dashboard = DeckDashboard(deck=deck, sections=request.data['dashboard'])
                dashboard.save()

        updateDeckCardsFromRequest(request, deck)
                    
        return Response({"message": "Deck added!", "deckId": deck.id}, status=status.HTTP_201_CREATED)
    
class DeckView(APIView):
    """

    """
    def get(self, request, deckId=None):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

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
                card.group = deckCardCountsMappedById[card.scryfallId].group
                mainBoard.append(card)
            if deckCardCountsMappedById[card.scryfallId].board == 'side':
                card.count = deckCardCountsMappedById[card.scryfallId].count
                card.group = deckCardCountsMappedById[card.scryfallId].group
                sideBoard.append(card)
            if deckCardCountsMappedById[card.scryfallId].board == 'maybe':
                card.count = deckCardCountsMappedById[card.scryfallId].count
                card.group = deckCardCountsMappedById[card.scryfallId].group
                maybeBoard.append(card)
            if deckCardCountsMappedById[card.scryfallId].board == 'acquire':
                card.count = deckCardCountsMappedById[card.scryfallId].count
                card.group = deckCardCountsMappedById[card.scryfallId].group
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

        if deck.user_id != request.user.id:
            return Response({"message": "You do not have permission to update this deck"}, status=status.HTTP_403_FORBIDDEN)

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

        if 'partnerId' in request.data:
            deck.partner = ScryfallCard.objects.get(scryfallId=request.data['partnerId'])

        if 'isKit' in request.data:
            deck.isKit = request.data['isKit']

        if 'inProgress' in request.data:
            deck.inProgress = request.data['inProgress']

        if 'kits' in request.data:
            deckKits = request.data['kits']
            deckKitLinks = DeckKitLink.objects.filter(deck_id=deckId).values_list('kit_id', flat = True)
            
            for kitId in deckKits:
                if kitId not in deckKitLinks:
                    deckKitLink = DeckKitLink(deck_id=deckId, kit_id=kitId)
                    deckKitLink.save()
            
            for kitId in deckKitLinks:
                if kitId not in deckKits:
                    deckKitLink = DeckKitLink.objects.filter(deck_id=deckId, kit_id=kitId)
                    deckKitLink[0].delete()

        deck.save()

        updateDeckCardsFromRequest(request, deck)

        return Response({"message": "Deck updated!"}, status=status.HTTP_200_OK)
    
    def delete(self, request, deckId):
        deck = Deck.objects.get(id=deckId)

        if deck.user_id != request.user.id:
            return Response({"message": "You do not have permission to delete this deck"}, status=status.HTTP_403_FORBIDDEN)

        deck.delete()

        return Response({"message": "Deck deleted!"}, status=status.HTTP_200_OK)

class UserDeckView(APIView):
    """

    """
    def get(self, request, userId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)

        page = int(request.query_params.get('page', 1))
        items = int(request.query_params.get('items', 50))

        includePrivate = True if request.query_params.get('includePrivate', False) else False
        search = request.query_params.get('search', None)
        deckFormat = request.query_params.get('deckFormat', None)
        cardNames = request.query_params.getlist('cardNames[]', None)
        sort = request.query_params.get('sort', None)

        onlyKits = True if request.query_params.get('onlyKits', False) == 'true' else False

        query = Q(user_id=userId)

        if includePrivate:
            query.add(Q(private=True) | Q(private=False), Q.AND)

        if search:
            query.add(Q(name__icontains=search), Q.AND)

        if deckFormat:
            query.add(Q(format=deckFormat), Q.AND)

        if onlyKits:
            query.add(Q(isKit=True), Q.AND)
        else:
            query.add(Q(isKit=False), Q.AND)

        if len(cardNames) > 0:
            query.add(Q(deckcard__name__in=cardNames), Q.AND)

        if userId != request.user.id:
            query.add(Q(inProgress=False), Q.AND)

        decks = DeckSerializer(
        Deck.objects
            .filter(query)
            .annotate(favorites=Count('deckfavorite'), views=Count('deckview'))
            .order_by(sort if sort else 'created')
            [(page-1)*items:page*items], 
            many=True
        ).data

        total = Deck.objects.filter(query).count()

        return Response({ 
            "meta": {
                "page": page,
                "items": items,

                "totalItems": total,
                "totalPages": ceil(total / items),
            }, 
            "data": decks 
        })
        
class UserDeckFavoritesView(APIView):
    """

    """
    def get(self, request, userId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)

        page = int(request.query_params.get('page', 1))
        items = int(request.query_params.get('items', 50))

        search = request.query_params.get('search', None)
        deckFormat = request.query_params.get('deckFormat', None)
        cardNames = request.query_params.getlist('cardNames[]', None)
        sort = request.query_params.get('sort', None)

        isKit = request.query_params.get('isKit', False)

        userDeckFavorites = DeckFavorite.objects.filter(user_id=userId)

        if userId != request.user.id:
            query.add(Q(inProgress=False), Q.AND)

        if len(userDeckFavorites) > 0:
            query = Q(id__in=userDeckFavorites.values('deck'))

            if search:
                query.add(Q(name__icontains=search), Q.AND)

            if deckFormat:
                query.add(Q(format=deckFormat), Q.AND)

            if isKit:
                query.add(Q(isKit=True), Q.AND)
            else:
                query.add(Q(isKit=False), Q.AND)

            if len(cardNames) > 0:
                query.add(Q(deckcard__name__in=cardNames), Q.AND)

            decks = DeckSerializer(
                Deck.objects
                    .filter(query)
                    .annotate(favorites=Count('deckfavorite'), views=Count('deckview'))
                    .order_by(sort if sort else 'created')
                    [(page-1)*items:page*items], 
                    many=True
                ).data

            total = Deck.objects.filter(query).count()

            return Response({ 
                "meta": {
                    "page": page,
                    "items": items,

                    "totalItems": total,
                    "totalPages": ceil(total / items),
                }, 
                "data": decks 
            })

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

class DeckKitsLinkView(APIView):
    """

    """
    def get(self, request, deckId):
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        deckKitLinks = DeckKitLink.objects.filter(deck_id=deckId)

        kitsFromLinks = Deck.objects.filter(id__in=deckKitLinks.values('kit'))

        return Response(DeckSerializer(kitsFromLinks, many=True).data)
