from django.db import models
from django.conf import settings

class Deck(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    private = models.BooleanField(default=True)


class DeckCard(models.Model):
    name = models.CharField(max_length=512)
    scryfall_id = models.CharField(max_length=512)
    count = models.IntegerField(default=1)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)


class Sideboard(models.Model):
    deck = models.OneToOneField(Deck, on_delete=models.CASCADE)

class SideboardCard(models.Model):
    name = models.CharField(max_length=512)
    scryfall_id = models.CharField(max_length=512)
    sideboard_deck = models.ForeignKey(Sideboard, on_delete=models.CASCADE)
