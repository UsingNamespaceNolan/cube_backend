from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from cube_app.models import (Deck, DeckCard, DeckChange, DeckDashboard,
                             DeckFavorite, DeckView, ScryfallCard)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] # map username to name ?

class NewUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=50)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user
    
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups', 'password']


class DeckSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()

    def get_favorites(self, instance):
        return DeckFavorite.objects.filter(deck=instance).count()
    
    def get_views(self, instance):
        return DeckView.objects.filter(deck=instance).count()

    class Meta:
        model = Deck
        fields = ['id', 'user', 'user_id', 'name', 'description', 'favorites', 'views', 'created', 'updated', 'format', 'colors', 'private', 'featuredArtUrl', 'commander']
        depth = 1

class DeckCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckCard
        fields = ['id', 'deck', 'scryfallId', 'name', 'count', 'board']

class DeckDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckDashboard
        fields = ['sections']

class DeckChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckChange
        fields = ['id', 'deck', 'name', 'count', 'board', 'timestamp']

class DeckFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckFavorite
        fields = ['id', 'deck', 'user']

class DeckViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeckView
        fields = ['id', 'deck', 'user']

class ScryfallCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScryfallCard
        fields = [
            'scryfallId',
            'count',
            'set',
            'setName',
            'collectorNumber',
            'releasedAt',
            'cardBackId',
            'artist',
            
            'name',
            'colors',
            'colorIdentity',
            'manaCost',
            'cmc',
            'rarity',
            'typeLine',
            'power',
            'toughness',
            'loyalty',
            'defense',
            'producedMana',
            'oracleText',
            'flavorText',
            
            'borderColor',
            'frame',
            'fullArt',
            'promo',
            'finishes',
            'foil',
            'nonfoil',
            'lang',
            
            'imageURIs',
            'faces',
            'prices',
            'priceUris',
            'legalities',
            'relatedUris',
            'allParts',
        ]


class TokenObtainPairSerializerWithUser(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add your extra responses here
        data['id'] = self.user.id
        data['name'] = self.user.username
        data['email'] = self.user.email
        return data