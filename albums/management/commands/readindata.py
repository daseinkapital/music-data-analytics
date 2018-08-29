from django.core.management.base import BaseCommand, CommandError
from albums.models import Artist, PrimaryGenre, SubGenre, Rating, Album , AlbumSubgenre

import csv
import datetime as dt

class Command(BaseCommand):
    help = 'Reads in data from the initial spreadsheet.'

    def handle(self, *args, **options):
        file = "NewAlbums.csv"
        with open(file, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            
            all_artists = []
            all_genres = []
            all_subgenres = []

            for row in csv_reader:
                all_artists.append(row['Artist'])
                all_genres.append(row['Primary Genre'])
                all_subgenres.append(row['Specific Genre'])
            
            all_subgenres = split_subgenres(list(set(all_subgenres)))



            unique_artists = list(set(all_artists))
            unique_genres = list(set(all_genres))
            unique_subgenres = list(set(all_subgenres))

            print(unique_subgenres)
            for artist in unique_artists:
                if artist == '':
                    continue
                else:
                    if Artist.objects.filter(name=artist).first():
                        continue
                    else:
                        Artist.objects.create(
                            name = artist
                        )
            
            for genre in unique_genres:
                if genre != '':
                    if PrimaryGenre.objects.filter(name=genre).first():
                        continue
                    else:
                        PrimaryGenre.objects.create(
                            name = genre
                        )

            for genre in unique_subgenres:
                if genre != '':
                    if SubGenre.objects.filter(name=genre).first():
                        continue
                    else:
                        SubGenre.objects.create(
                            name = genre
                        )

        with open(file, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            for row in csv_reader:
                print(row)
                artist = Artist.objects.filter(name=row['Artist']).first()
                primary_genre = PrimaryGenre.objects.filter(name=row['Primary Genre']).first()
                album = Album.objects.filter(artist=artist, name=row['Album']).first()
                if not album:
                    album = Album.objects.create(
                        name = row['Album'],
                        artist = artist,
                        order = row['Order'],
                        chart = row['Chart'],
                        row = row['Row'],
                        date_finished = convert_date(row['Date Finished']),
                        primary_genre = primary_genre,
                    )

                    if row['Ratings by Listen']:
                        Rating.objects.create(
                            score = row['Ratings by Listen'],
                            listen = 1,
                            album = album
                        )

                    if row['Specific Genre']:
                        if '/' in row['Specific Genre']:                
                            subgenres = row['Specific Genre'].split('/')
                            if album:
                                for subgenre in subgenres:
                                    subgenre = SubGenre.objects.filter(name=subgenre).first()
                                    AlbumSubgenre.objects.create(
                                        album=album,
                                        subgenre=subgenre
                                    )
                        else:
                            subgenre = row['Specific Genre']
                            if album:
                                subgenre = SubGenre.objects.filter(name=subgenre).first()
                                AlbumSubgenre.objects.create(
                                    album=album,
                                    subgenre=subgenre
                                )


def split_subgenres(subgenres):
    for row in subgenres:
        if "/" in row:
            while row in subgenres:
                subgenres.remove(row)        
            new_genres = row.split("/")
            for genre in new_genres:
                subgenres.append(genre)
    return subgenres

def convert_date(date_str):
    if date_str:
        return dt.datetime.strptime(date_str, '%m/%d/%Y')
    else:
        return None