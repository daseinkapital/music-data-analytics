import os

from albums.models import *
from django.db.models import Avg, Sum
from datetime import datetime, date
import pandas as pd
from django.urls import reverse
from django.utils.http import urlencode

class YearStats:
    def __init__(self):
        self.year = self.get_year()
        self.albums = self.get_albums()
        self.album_qty = len(self.albums)
        self.time_listened = self.calculate_time_listened()

    def get_year(self):
        year = date.today().year

        # if it's before march, continue to show last year's stats
        if date.today().month < 4:
            year -= year

        return year 

    def get_albums(self):
        year_albums = Album.objects.filter(date_finished__year=self.year)
        return year_albums
    
    def calculate_time_listened(self):
        time = dt.timedelta(seconds=0)
        for album in self.albums:
            if album.time_length:
                time += album.time_length

        total_time = time.total_seconds()
        
        return round(total_time/60)
    
    def json_albums(self):
        albums = pd.DataFrame(
            Album.objects.filter(
                date_finished__year=self.year
            ).values(
                'slug',
                'name',
                'date_finished',
                'current_rating',
                'artist'
            )
        )
        reload_data = True
        if os.path.exists('./year_in_review_{}.json'.format(self.year)):
            file_albums = pd.read_json('./year_in_review_{}.json'.format(self.year))
            if len(albums) == len(file_albums):
                reload_data = False
                albums = file_albums
        if reload_data:
            artists = Artist.objects.all()
            albums['name'] = albums.apply(lambda row: row['name'].replace('"', "'"), axis=1)
            albums['date_finished'] = albums.apply(lambda row: row['date_finished'].strftime('%m-%d-%Y'), axis=1)
            albums['artist_slug'] = albums.apply(lambda row: artists.filter(id=row['artist']).first().slug, axis=1)
            albums['artist'] = albums.apply(lambda row: artists.filter(id=row['artist']).first().name, axis=1)
            albums['artist_url'] = albums.apply(lambda row: self.make_reverse(row, t='artist'), axis=1)
            albums['album_url'] = albums.apply(lambda row: self.make_reverse(row), axis=1)
            albums = albums.drop(columns=['artist_slug', 'slug'])
            albums.to_json('./year_in_review_{}.json'.format(self.year), orient='records')

        return albums.to_json(orient='records')

    def make_reverse(self, row, t='album'):
        if t == 'album':
            return reverse('album-page', args=[row['artist_slug'], row['slug']])
        else:
            return reverse('artist-page', args=[row['artist_slug']])