import uuid
from django.db import models
from django.conf import settings

class Deck(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class DeckCard(models.Model):
    name = models.CharField(max_length=512)
    scryfall_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)


class Sideboard(models.Model):
    deck = models.OneToOneField(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(DeckCard, on_delete=models.CASCADE)

