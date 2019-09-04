from django.core.management.base import BaseCommand, CommandError
from albums.models import Album

import urllib.parse
import urllib.request
import spotipy
import spotipy.util as util
import json

import os

class Command(BaseCommand):
    help = "Finds my Spotify Playlists that contain a song from each album"

    def handle(self, *args, **options):
        print("Updating playlist file")
        get_all_my_playlists(update_file=True)
        print("All playlist songs updated")
        print("Updating album playlists")
        for album in Album.objects.all():
            if album.spotify_url:
                print("Current album", album)
                find_album_in_playlist(album, overwrite_current_playlist=True)
                

############ SPOTIFY FUNCTIONS ####################
#move these once active listening is done
def find_album_in_playlist(album, spotify_session=None, overwrite_current_playlist=False):
    album_id = False
    if album.spotify_url:
        url_check = album.spotify_url.find('album/')
        if url_check > 0: #ensure that scraping didn't accidentally find the artist
            album_id = album.spotify_url[url_check+6:]

    if album.playlists and not overwrite_current_playlist:
        return album.playlists

    if album_id:
        if not spotify_session:
            sp = init_spotify_creds()
        else:
            sp = spotify_session

        if sp:
            full_album_info = sp.album(album_id)
            tracks = []
            playlists_to_skip = [ #for my own sake...
                'Anika',
                'Music To Figure Out If I Like',
                'G-Lit-T',
                'Stuttering',
                'MOAR COWBELL',
                'To Ryan, From Andrew',
                'Second Listen',
                '90s and On',
                '80s and Oldies'
            ]

            for song in full_album_info['tracks']['items']:
                tracks.append({'artist': song['artists'][0]['name'], 'name': song['name']})
            
            data = get_all_my_playlists(spotify_session=sp)
            
            to_remove = []
            for playlist in data:
                if playlist['name'] in playlists_to_skip:
                    to_remove.append(playlist)
            for playlist in to_remove:
                data.remove(playlist)
            
            matches = []
            for playlist in data:
                info = {
                    'playlist_name': playlist['name'],
                    'url': playlist['url']
                }
                keep_searching = True
                for track1 in tracks:
                    if not keep_searching:
                        break
                    for track2 in playlist['tracks']:
                        if tracks_match(track1, track2):

                            # need this block because I have duplicated playlists for organizational purposes
                            playlist_already_added = False
                            for match in matches:
                                if info['playlist_name'] == match['playlist_name']:
                                    playlist_already_added = True
                            if not playlist_already_added:
                                matches.append(info)
                            keep_searching = False
                            break
                            
            album.playlists = json.dumps(matches)
            album.save()


def tracks_match(track1, track2):
    if track1['artist'] == track2['artist'] and (track1['name'] in track2['name'] or track2['name'] in track1['name']):
        return True
    return False


def get_all_my_playlists(spotify_session=None, update_file=False):
    file = "all_playlist_tracks"
    if os.path.exists(file + ".json") and not update_file:
        return read_from_json(file)

    if not spotify_session:
        sp = init_spotify_creds()
    else:
        sp = spotify_session
    
    if sp:
        playlists = sp.user_playlists(os.environ['SPOTIFY_USERNAME'])
        reduced_playlists = []
        while playlists:
            for playlist in playlists['items']:
                if playlist['owner']['id'] == os.environ['SPOTIFY_USERNAME']:
                    info = {
                        'url': playlist['external_urls']['spotify'],
                        'name': playlist['name'],
                        'total_tracks': playlist['tracks']['total'],
                        'id': playlist['id']
                    }
                    tracks = sp.user_playlist_tracks(os.environ['SPOTIFY_USERNAME'], playlist_id=info['id'])
                    
                    playlist_tracks = []
                    while tracks:
                        for track in tracks['items']:
                            playlist_tracks.append({
                                'name': track['track']['name'],
                                'artist': track['track']['artists'][0]['name']
                            })
                        tracks = sp.next(tracks)
                    info.update({'tracks': playlist_tracks})
                    reduced_playlists.append(info)
            playlists = sp.next(playlists)            
        write_to_json(reduced_playlists, file)
        return reduced_playlists

def write_to_json(data, filename):
    filename += '.json'
    with open(filename, 'w') as file:
        json.dump(data, file)
    file.close()
    print("{} printed".format(filename))


def read_from_json(filename):
    filename += '.json'
    if os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)
    else:
        return None


def init_spotify_creds():
    scope = 'user-library-read'
    spotify_username = os.environ['SPOTIFY_USERNAME']
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    redirect_uri = 'http://localhost:8000/'
    token = util.prompt_for_user_token(spotify_username, scope, client_id, client_secret, redirect_uri)
    if token:
        return spotipy.Spotify(auth=token)
    else:
        return None