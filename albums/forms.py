from django.forms import ModelForm
from django import forms

from albums.models import Album


#MODEL CLASSES
class AlbumForm(ModelForm):
    rating = forms.DecimalField(label="Rating", required=False)
    subgenres = forms.CharField(label="Subgenres", required=False, widget=forms.Textarea)

    class Meta:
        model = Album
        fields = [
            'name',
            'artist',
            'date_finished',
            'primary_genre',
            'wiki_url',
            'bc_url',
            'amazon_url',
            'time_length',
            'release_date',
            'album_art',
            'vinyl',
            'cassette',
            'rating',
            'subgenres'
        ]

#OTHER FORMS
class ReccForm(forms.Form):
    recc_name = forms.CharField(label="Your Name", required=True)
    album_name = forms.CharField(label="Album", required=True)
    artist_name = forms.CharField(label="Artist", required=True)
    genre = forms.CharField(label="Genre", required=False)
    url = forms.CharField(label="Album Info", help_text="This could be a Wikipedia/Bandcamp/Amazon link etc. that has information about the album", required=False)
    note = forms.CharField(label="Reason for Recommendation", help_text="Tell me why you're recommending me this album!", widget=forms.Textarea)

    class Meta:
        fields = [
            'recc_name,'
            'album_name',
            'artist_name',
            'genre',
            'url',
            'note'
        ]

        fields_required = [
            'recc_name',
            'album_name',
            'artist_name'
        ]