from django import forms

class DeckRequestForm(forms.Form):
    deck_name = forms.CharField(max_length=255)