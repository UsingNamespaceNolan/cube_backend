from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from cube_app.models import Deck

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
    class Meta:
        model = Deck
        fields = ['id', 'name', 'user', 'private']


class TokenObtainPairSerializerWithUser(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add your extra responses here
        data['id'] = self.user.id
        data['name'] = self.user.username
        data['email'] = self.user.email
        return data