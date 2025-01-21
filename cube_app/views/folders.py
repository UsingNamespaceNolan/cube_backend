from math import ceil
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Deck, Folder
from ..serializers import FolderSerializer

class FoldersView(APIView):
    """

    """
    def get(self, request, userId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        page = request.query_params.get('page', 1)
        items = request.query_params.get('items', 10)
        
        search = request.query_params.get('search', None)
        sort = request.query_params.get('sort', None)

        query = Q(user_id=userId)

        if search:
            query.add(Q(name__icontains=search), Q.AND)

        folders = Folder.objects.filter(query)
        total = folders.count()

        return Response({ 
                "meta": {
                    "page": page,
                    "items": items,

                    "totalItems": total,
                    "totalPages": ceil(total / items),
                }, 
                "data": FolderSerializer(folders, many=True).data
            })
    
    def post(self, request, userId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get('name', "New Folder")

        folder = Folder(user_id=userId, name=name)
        folder.save()

        return Response({"message": "Folder created!", "folderId": folder.id}, status=status.HTTP_201_CREATED)

class FolderView(APIView):
    """

    """
    def get(self, request, userId, folderId=None):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not folderId:
            return Response({"message": "Provide a folder id!"}, status=status.HTTP_400_BAD_REQUEST)

        folders = Folder.objects.filter(id=folderId, user_id=userId)

        return Response(FolderSerializer(folders, many=True).data[0])
    
    def patch(self, request, userId, folderId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not folderId:
            return Response({"message": "Provide a folder id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        name = request.data.get('name', None)

        if not name:
            return Response({"message": "Provide a name!"}, status=status.HTTP_400_BAD_REQUEST)

        folder = Folder.objects.get(id=folderId, user_id=userId)

        folder.name = name;
        
        folder.save()

        return Response({"message": "Folder updated!"}, status=status.HTTP_200_OK)
    
    def delete(self, request, userId, folderId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not folderId:
            return Response({"message": "Provide a folder id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        folder = Folder.objects.get(id=folderId, user_id=userId)
        folder.delete()

        return Response({"message": "Folder deleted!"}, status=status.HTTP_200_OK)
    
    
class FolderDecksView(APIView):
    """

    """
    def post(self, request, userId, folderId, deckId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not folderId:
            return Response({"message": "Provide a folder id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        folder = Folder.objects.get(id=folderId, user_id=userId)
        folderDecks = Deck.objects.filter(id__in=folder.decks.values('id'))

        for deck in folderDecks:
            if deck.id == deckId:
                return Response({"message": "Deck already in folder!"}, status=status.HTTP_400_BAD_REQUEST)

        folder.decks.add(deckId)

        folder.save()

        return Response({"message": "Folder updated!"}, status=status.HTTP_200_OK)

    def delete(self, request, userId, folderId, deckId):
        if not userId:
            return Response({"message": "Provide a user id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not folderId:
            return Response({"message": "Provide a folder id!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not deckId:
            return Response({"message": "Provide a deck id!"}, status=status.HTTP_400_BAD_REQUEST)

        folder = Folder.objects.get(id=folderId, user_id=userId)
        folderDecks = Deck.objects.filter(id__in=folder.decks.values('id'))

        for deck in folderDecks:
            if deck.id == deckId:
                folder.decks.remove(deckId)
                break

        folder.save()

        return Response({"message": "Folder updated!"}, status=status.HTTP_200_OK)