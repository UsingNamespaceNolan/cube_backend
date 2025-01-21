
from cube_app.models import DeckCard, DeckChange

def updateDeckCardsFromRequest(request, deck):
    cards = request.data.get('cards', [])

    updateDeckCards(cards, deck)

def updateDeckCards(deckCards, deck):
    cards = []

    for card in deckCards:
        cards.append(DeckCard(
            deck=deck, 
            scryfallId=card['scryfallId'], 
            name=card['name'],
            count=int(card['count']),
            group=card.get('group'), 
            board=card['board'],
        ))

    oldCards = list(DeckCard.objects.filter(deck=deck))

    boards = ['main', 'side', 'maybe', 'acquire']

    for board in boards:
        cardsInBoard = [card for card in cards if card.board == board]
        oldCardsInBoard = [card for card in oldCards if card.board == board]

        newCards, changedCards, modifiedCards, removedCards = getCardDifferences(deck, cardsInBoard, oldCardsInBoard)

        DeckCard.objects.bulk_create(newCards)
        DeckCard.objects.bulk_update(modifiedCards, ['scryfallId', 'count', 'group', 'board'])
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
                if newCard.count != oldCard.count:
                    newCard.id = oldCard.id
                    modifiedCards.append(newCard)
                    changedCards.append(DeckChange(
                        deck = deck,
                        name = newCard.name,
                        count = newCard.count - oldCard.count,
                        board = newCard.board,
                    ))
                elif newCard.group != oldCard.group or newCard.scryfallId != oldCard.scryfallId:
                    newCard.id = oldCard.id
                    modifiedCards.append(newCard)
                    
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