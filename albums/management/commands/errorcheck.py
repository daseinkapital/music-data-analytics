from django.core.management.base import BaseCommand, CommandError
from albums.models import Album, Artist

import datetime as dt

class Command(BaseCommand):
    help = 'Checks for errors after a run of adddata.'

    def handle(self, *args, **options):
        albums = Album.objects.all()

        missing_art = []
        missing_time = []
        missing_release = []
        zero_time = []
        misidentification_of_time = []
        album_art_duplicate = []
        for album in albums:
            if album.album_art == None:
                missing_art.append(album)
            if album.time_length == None:
                missing_time.append(album)
            if album.release_date == None:
                missing_release.append(album)
            if album.time_length != None:
                if album.time_length == dt.timedelta(seconds=0):
                    zero_time.append(album)
                if album.time_length < dt.timedelta(minutes=10):
                    misidentification_of_time.append(album)
            
            for other_album in Album.objects.all():
                if (album.album_art == other_album.album_art) and (album not in missing_art) and (str(album) != str(other_album)):
                    album_art_duplicate.append({'album' : album, 'match' : other_album})

        output("Albums missing art", missing_art)
        output("Albums missing time length", missing_time)
        output("Albums missing release date", missing_release)
        output("Albums with no time", zero_time)
        output("Possibly misidentified times", misidentification_of_time)

        if album_art_duplicate:
            print("\nAlbum duplicates")
            for album in album_art_duplicate:
                print(str(album['album']) + " matched with " + str(album['match']))

def output(message, albums):
    if albums:
        print("\n" + message)
        for album in albums:
            print(album)