from django.contrib.auth.models import User
from rest_framework import serializers

from cube_app.models import Deck

class NewUserSerializer(serializers.HyperlinkedModelSerializer):
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