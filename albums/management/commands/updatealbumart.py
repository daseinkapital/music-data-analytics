from django.core.management.base import BaseCommand, CommandError
from albums.models import Album

from .scrape import fetch_url, screw_the_rules, bc_album_art, sc_album_art, amazon_album_art, itunes_album_art, spotify_album_art

class Command(BaseCommand):
    help = 'Runs through other sites and sees if a better image exists than the wikipedia image.'

    def handle(self, *args, **options):
        albums = Album.objects.filter(wiki_url__icontains='//upload')
        for album in albums:
            print(album)
            wiki_art = album.album_art
            album.album_art = None
            if album.bc_url:
                album = bc_album_art(album)
                album.save()
                print("Successfully updated with Bandcamp!")
            if not album.album_art_check():
                if album.sc_url:
                    album = sc_album_art(album)
                    album.save()
                    print("Successfully updated with SoundCloud!")
            if not album.album_art_check():
                if album.itunes_url:
                    album = itunes_album_art(album)
                    album.save()
                    print("Successfully updated with iTunes!")
            if not album.album_art_check():
                if album.spotify_url:
                    album = spotify_album_art(album)
                    album.save()
                    print("Successfully updated with Spotify!")
            if not album.album_art_check():
                if album.amazon_url:
                    album = amazon_album_art(album)
                    album.save()
                    print("Successfully updated with Amazon!")
            if not album.album_art_check():
                album.album_art = wiki_art
                print("No matches. Reverting to wikipedia art.")
                album.save()