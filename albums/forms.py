from django.forms import ModelForm
from albums.models import Album


class AlbumForm(ModelForm):
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
            'cassette'
        ]