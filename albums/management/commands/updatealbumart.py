from django.core.management.base import BaseCommand, CommandError
from albums.models import Album

import urllib.parse
import urllib.request

from .scrape import fetch_url, screw_the_rules, bc_album_art, sc_album_art, amazon_album_art, itunes_album_art, spotify_album_art

class Command(BaseCommand):
    help = 'Runs through other sites and sees if a better image exists than the wikipedia image.'

    def handle(self, *args, **options):
        screw_the_rules()
        albums = Album.objects.filter(album_art__icontains='//upload')
        for album in albums:
            print(album)
            wiki_art = album.album_art
            album.album_art = None
            if album.bc_url:
                try:
                    url = album.bc_url
                    html = fetch_url(url)
                    album.album_art = bc_album_art(html)
                    album.save()
                    print("Successfully updated with Bandcamp!")

                except(urllib.error.HTTPError):
                    print('Error with page.')
            if not album.album_art_check():
                if album.itunes_url:
                    try:
                        url = album.itunes_url
                        html = fetch_url(url)
                        album.album_art = itunes_album_art(html)
                        album.save()
                        print("Successfully updated with iTunes!")

                    except(urllib.error.HTTPError):
                        print('Error with page.')
            if not album.album_art_check():
                if album.spotify_url:
                    try:
                        url = album.spotify_url
                        html = fetch_url(url)
                        album.album_art = spotify_album_art(html)
                        album.save()
                        print("Successfully updated with Spotify!")

                    except(urllib.error.HTTPError):
                        print('Error with page.')
            if not album.album_art_check():
                if album.amazon_url:
                    try:
                        url = album.amazon_url
                        html = fetch_url(url)
                        album.album_art = amazon_album_art(html)
                        album.save()
                        print("Successfully updated with Amazon!")

                    except(urllib.error.HTTPError):
                        print('Error with page.')
            if not album.album_art_check():
                if album.soundcloud_url:
                    try:
                        url = album.soundcloud_url
                        html = fetch_url(url)
                        album.album_art = sc_album_art(html)
                        album.save()
                        print("Successfully updated with SoundCloud!")

                    except(urllib.error.HTTPError):
                        print('Error with page.')
            if not album.album_art_check():
                album.album_art = wiki_art
                print("No matches. Reverting to wikipedia art.")
                album.save()