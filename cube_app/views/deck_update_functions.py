
from cube_app.models import DeckCard, DeckChange


def updateDeckCards(request, deck):
    cards = []
    scryfallIds = set()
    
    for card in request.data['cards']:
        if card['scryfallId'] not in scryfallIds:
            cards.append(DeckCard(
                deck=deck, 
                scryfallId=card['scryfallId'], 
                name=card['name'],
                count=int(card['count']),
                board=card['board'],
            ))

    oldCards = list(DeckCard.objects.filter(deck=deck))
    newCards, changedCards, modifiedCards, removedCards = getCardDifferences(deck, cards, oldCards)

    DeckCard.objects.bulk_create(newCards)
    DeckCard.objects.bulk_update(modifiedCards, ['count'])
    deleteIds = [card.id for card in removedCards]
    DeckCard.objects.filter(id__in=deleteIds).delete()

    createCardChanges(deck, newCards, changedCards, removedCards)


def getCardDifferences(deck, newCards, oldCards):
    addedCards = []
    modifiedCards = []
    changedCards = []
    removedCards = []

    for newCard in newCards:
        foundCard = False

        for oldCard in oldCards:
            if newCard.name == oldCard.name:
                if newCard.count != oldCard.count or newCard.scryfallId != oldCard.scryfallId:
                    newCard.id = oldCard.id
                    modifiedCards.append(newCard)
                    changedCards.append(DeckChange(
                        deck = deck,
                        name = newCard.name,
                        count = newCard.count - oldCard.count,
                        board = newCard.board,
                    ))
                foundCard = True
                break

        if not foundCard:
            addedCards.append(newCard)

    for oldCard in oldCards:
        foundCard = False

        for newCard in newCards:
            if oldCard.name == newCard.name:
                foundCard = True
                break

        if not foundCard:
            removedCards.append(oldCard)

    return addedCards, changedCards, modifiedCards, removedCards

def createCardChanges(deck, newCards, changedCards, removedCards):
    newCardChanges = []
    for card in newCards:
        newCardChanges.append(DeckChange(
            deck=deck,
            name=card.name,
            count=card.count,
            board=card.board,
        ))

    deleteCardChanges = []
    for card in removedCards:
        deleteCardChanges.append(DeckChange(
            deck=deck,
            name=card.name,
            count=card.count * -1,
            board=card.board,
        ))

    DeckChange.objects.bulk_create(newCardChanges)
    DeckChange.objects.bulk_create(changedCards)
    DeckChange.objects.bulk_create(deleteCardChanges)