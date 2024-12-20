
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ScryfallCard


class ScryfallCardView(APIView):
    def post(self, request):
        print('Scryfall')
        
        if 'cards' not in request.data:
            return Response({"message": "Provide a list of cards!"}, status=status.HTTP_400_BAD_REQUEST)

        cards = request.data['cards']

        index = 0
        cardsToAdd = []
        for card in cards:
            print(index, 'Adding:', card['name'])
            index += 1
            cardsToAdd.append(
                ScryfallCard(
                    scryfallId=card.get('id'),
                    set=card.get('set'),
                    setName=card.get('set_name'),
                    collectorNumber=card.get('collector_number'), 
                    releasedAt=card.get('released_at'),
                    cardBackId=card.get('card_back_id'), 
                    artist=card.get('artist'),

                    name=card.get('name'), 
                    colors=card.get('colors'), 
                    colorIdentity=card.get('color_identity'),
                    manaCost=card.get('mana_cost'),
                    cmc=card.get('cmc'),
                    rarity=card.get('rarity'),
                    typeLine=card.get('type_line'),
                    power=card.get('power'),
                    toughness=card.get('toughness'),
                    loyalty=card.get('loyalty'),
                    defense=card.get('defense'),
                    producedMana=card.get('produced_mana'),
                    oracleText=card.get('oracle_text'),
                    flavorText=card.get('flavor_text'),
                    
                    borderColor=card.get('border_color'),
                    frame=card.get('frame'),
                    fullArt=card.get('full_art'),
                    promo=card.get('promo'),
                    finishes=card.get('finishes'),
                    foil=card.get('foil'),
                    nonfoil=card.get('nonfoil'),
                    lang=card.get('lang'),
                    
                    imageURIs=card.get('image_uris'),
                    faces=card.get('card_faces'),
                    prices=card.get('prices'),
                    priceUris=card.get('purchase_uris'),
                    legalities=card.get('legalities'),
                    relatedUris=card.get('related_uris'),
                    allParts=card.get('all_parts'),
                )
            )

        print('Creating cards...')
        ScryfallCard.objects.bulk_create(
            objs=cardsToAdd,
            update_fields=[
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
            ],
            # update_conflicts=True,
        )

        print('Done!')

        return Response({"message": "Cards added!"}, status=status.HTTP_201_CREATED)
