from django.core.management.base import BaseCommand, CommandError
from albums.models import Album, Artist, AlbumArtist

import urllib.parse
import urllib.request

import spotipy
import spotipy.util as util

import os
import datetime as dt
import time

from .scrape import scrape
from .checkurls import check_urls

class Command(BaseCommand):
    help = 'Check my spotify playlist of music to listen to and determine if there have been new songs added.'

    def handle(self, *args, **options):
        scope = 'user-library-read'
        spotify_username = os.environ['SPOTIFY_USERNAME']
        client_id = os.environ['SPOTIFY_CLIENT_ID']
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
        redirect_uri = 'http://localhost:8000/'
        token = util.prompt_for_user_token(spotify_username, scope, client_id, client_secret, redirect_uri)

        if token:
            sp = spotipy.Spotify(auth=token)
            queue_playlist = sp.user_playlist(spotify_username, playlist_id='spotify:playlist:6j3ksyq3Kp74CUpvymYciF')
            
            # create cutoff date because spotify api currently has a glitch
            # where it will show songs that were removed from spotify but
            # once in your playlist as still in your playlist 
            cutoff_date = dt.datetime(2019,3,1)
            all_songs = get_all_relevant_song_info(sp, queue_playlist, cutoff_date)
            
            albums_in_queue = get_list_of_all_albums_in_queue(all_songs)

            most_recent_album = get_most_recent_queue_album()

            unadded_albums = get_unadded_album(albums_in_queue, most_recent_album)
            
            for album in unadded_albums:
                str_album = "{0} by {1}".format(album['album'], album['artist'])
                print("Adding " + str_album)
                create_and_scrape_album(album)

        else:
            print("Can't get token for", spotify_username)





def get_all_relevant_song_info(spotify_player, playlist, cutoff_date):
    all_songs = []
    while playlist:
        for song in playlist['tracks']['items']:
            one_song = {}
            for key, val in song.items():
                if key == 'added_at':
                    date_added = dt.datetime.strptime(val, '%Y-%m-%dT%H:%M:%SZ')
                    one_song['date'] = date_added
                if key == 'track':
                    one_song['name'] = val['name']
                    one_song['album'] = val['album']['name']
                    one_song['artist'] = val['artists'][0]['name']
                    one_song['release_date'] = cleanse_date(val['album']['release_date'])
                    one_song['album_url'] = val['album']['external_urls']['spotify']
                    for image in val['album']['images']:
                        if image['height'] > 500:
                            one_song['cover_art'] = image['url']
                            break
            if one_song['date'] > cutoff_date:
                all_songs.append(one_song)
        if playlist['tracks']['next']:
            playlist['tracks'] = spotify_player.next(playlist['tracks'])
        else:
            playlist = None
    return all_songs

def cleanse_date(date):
    start = date.find('-')
    end = date.rfind('-')
    if start == -1:
        date = date + '-12-31'
    elif start == end:
        date = date + '-28'
    return date

def get_most_recent_queue_album():
    return Album.objects.filter(date_finished=None).order_by('id').last()

def get_list_of_all_albums_in_queue(queue_songs):
    albums = []
    album_info = []
    for song in queue_songs:
        if song['album'] not in albums:
            song.pop('name')
            song.pop('date')
            albums.append(song['album'])
            album_info.append(song)
    if len(albums) == len(album_info):
        return album_info
    else:
        print("Mismatch in algorithm for queue albums")
        return

def get_unadded_album(album_info, most_recent_queue_album):
    most_recent = str(most_recent_queue_album)

    for i, album in enumerate(album_info):
        str_album = "{0} by {1}".format(album['album'], album['artist'])
        if str_album == most_recent:
            return album_info[i+1:]

def create_and_scrape_album(album):
    # either get the artist or create a new one
    # in the future this should keep artists more consistent
    artist = Artist.objects.filter(name__iexact=album['artist']).first()
    if not artist:
        artist = Artist.objects.create(name=album['artist'])

    new_album = Album.objects.create(
        name = album['album'],
        artist = artist,
        spotify_url = album['album_url'],
        release_date = album['release_date'],
    )

    if album['cover_art']:
        new_album.album_art = album['cover_art']

    AlbumArtist.objects.create(
        album=new_album,
        artist=artist
    )

    new_album.save()
    check_urls(new_album)
    scrape(new_album, search_for_urls=True)