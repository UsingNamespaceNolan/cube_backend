"""
URL configuration for cube_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from cube_app import views

router = routers.DefaultRouter()

urlpatterns = [
    path('api/set-csrf-cookie/', views.set_csrf_token, name='Set-CSRF'),
    path('', include(router.urls)),

    # User endpoints
    path('api/users/current/', views.CurrentUserView.as_view(), name='current_user'),
    path('api/users/register/', views.RegisterUserView.as_view(), name='register'),
    path('api/users/logout/', views.LogoutView.as_view(), name='api_logout'),

    # Token endpoints
    path('api/users/login/', views.TokenObtainPairWithUser.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Deck endpoints
    path('api/decks/', views.DeckView.as_view(), name='deck'),
    path('api/decks/public/', views.DeckViewPublic.as_view(), name='deck'),
    path('api/decks/<int:deckId>/changes/', views.DeckChangeView.as_view(), name='deck_change'),

    # Scryfall endpoints
    path('api/scryfall/', views.ScryfallCardView.as_view(), name='scryfall_card'),
]
