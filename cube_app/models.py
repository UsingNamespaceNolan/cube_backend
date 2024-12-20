from django.conf import settings
from django.db import models


class ScryfallCard(models.Model):
    # Card Info
    scryfallId = models.CharField(primary_key=True, max_length=512)
    count = models.IntegerField(default=0)
    set = models.CharField(max_length=512, default=None, null=True)
    setName = models.CharField(max_length=512, default=None, null=True)
    collectorNumber = models.CharField(max_length=512, default=None, null=True)
    releasedAt = models.DateField(default=None, null=True)
    cardBackId = models.CharField(max_length=512, default=None, null=True)
    artist = models.CharField(max_length=512, default=None, null=True)

    # Card Details
    name = models.CharField(max_length=512, default=None, null=True)
    colors = models.CharField(max_length=512, default=None, null=True)
    colorIdentity = models.CharField(max_length=512, default=None, null=True)
    manaCost = models.CharField(max_length=512, default=None, null=True)
    cmc = models.IntegerField(default=0, null=True)
    rarity = models.CharField(max_length=512, default=None, null=True)
    typeLine = models.CharField(max_length=512, default=None, null=True)
    power = models.CharField(max_length=512, default=None, null=True)
    toughness = models.CharField(max_length=512, default=None, null=True)
    loyalty = models.CharField(max_length=512, default=None, null=True)
    defense = models.CharField(max_length=512, default=None, null=True)
    producedMana = models.CharField(max_length=512, default=None, null=True)
    oracleText = models.CharField(max_length=512, default=None, null=True)
    flavorText = models.CharField(max_length=512, default=None, null=True)

    # Print Info
    borderColor = models.CharField(max_length=512, default=None, null=True)
    frame = models.CharField(max_length=512, default=None, null=True)
    fullArt = models.BooleanField(default=False, null=True)
    promo = models.BooleanField(default=False, null=True)
    finishes = models.CharField(max_length=512, default=None, null=True)
    foil = models.BooleanField(default=False, null=True)
    nonfoil = models.BooleanField(default=False, null=True)
    lang = models.CharField(max_length=512, default=None, null=True)
    
    # Card Links
    imageURIs = models.JSONField(default=None, null=True)
    faces = models.JSONField(default=None, null=True)
    prices = models.JSONField(default=None, null=True)
    priceUris = models.JSONField(default=None, null=True)
    legalities = models.JSONField(default=None, null=True)
    relatedUris = models.JSONField(default=None, null=True)
    allParts = models.JSONField(default=None, null=True)

class Deck(models.Model):
    name = models.CharField(max_length=255, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=True)
    description = models.CharField(max_length=512, default=None)
    colors = models.CharField(max_length=512, default=None)
    featuredArtUrl = models.CharField(max_length=512, default=None)
    format = models.CharField(max_length=512, default=None)
    commander = models.ForeignKey(ScryfallCard, default=None, blank=True, null=True, on_delete=models.DO_NOTHING)

class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, default=None, on_delete=models.CASCADE)
    scryfallId = models.CharField(max_length=512, default=None)
    name = models.CharField(max_length=512, default=None)
    count = models.IntegerField(default=1)
    board = models.CharField(max_length=512, default=None)

class DeckDashboard(models.Model):
    deck = models.OneToOneField(Deck, default=None, on_delete=models.CASCADE)
    sections = models.JSONField(default=None)

class DeckChange(models.Model):
    deck = models.ForeignKey(Deck, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=512, default=None)
    count = models.IntegerField(default=0)
    board = models.CharField(max_length=512, default=None)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class DeckFavorite(models.Model):
    deck = models.ForeignKey(Deck, default=None, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE, related_name='favorites')

class DeckView(models.Model):
    deck = models.ForeignKey(Deck, default=None, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE, related_name='views')