from django.core.management.base import BaseCommand, CommandError
from albums.models import Artist, PrimaryGenre, SubGenre, Rating, Album , AlbumSubgenre

import csv
import datetime as dt

class Command(BaseCommand):
    help = 'Reads in data from the old albums list.'

    def handle(self, *args, **options):
        file = "OldAlbums.csv"
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

            save_objects(unique_artists, Artist)
            save_objects(unique_genres, PrimaryGenre)
            save_objects(unique_subgenres, SubGenre)

        clean_up()

        with open(file, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            for row in csv_reader:
                print(row)
                artist = Artist.objects.filter(name=row['Artist']).first()
                primary_genre = PrimaryGenre.objects.filter(name=row['Primary Genre']).first()
                album = Album.objects.filter(artist__name=row['Artist'], name=row['Album']).first()
                if not album:
                    album = Album.objects.create(
                        name = row['Album'],
                        artist = artist,
                        order = 0,
                        chart = 0,
                        row = 0,
                        date_finished = convert_date("1/1/2016"),
                        primary_genre = primary_genre,
                    )

                    if row['Specific Genre']:
                        if '/' in row['Specific Genre']:               
                            subgenres = row['Specific Genre'].split('/')
                            if album:
                                for genre in subgenres:
                                    subgenre = SubGenre.objects.filter(name=genre).first()
                                    if genre and not subgenre:
                                        subgenre = SubGenre.objects.create(name=genre)
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
                    album.save()
def save_objects(unique_set, model):
    for item in unique_set:
        if item != '':
            if model.objects.filter(name=item).first():
                continue
            else:
                model.objects.create(
                    name = item
                )

def split_subgenres(subgenres):
    for row in subgenres:
        if "/" in row:
            new_genres = row.split("/")
            for genre in new_genres:
                subgenres.append(genre)
            while row in subgenres:
                subgenres.remove(row)        
            
    return subgenres

def convert_date(date_str):
    if date_str:
        return dt.datetime.strptime(date_str, '%m/%d/%Y')
    else:
        return None

def clean_up():
    for obj in SubGenre.objects.filter(name__contains="/"):
        obj.delete()