from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import random, os


import spotipy
from spotipy import oauth2

def current_user_playing_track(self):
    ''' Get information about the current users currently playing track.
    '''
    return self._get('me/player/currently-playing')



def experimental_features(request):
    context = {}
    if os.environ['ENVIRON_SETTING'] == 'dev':
        url_base = 'http://localhost:8000'
    else:
        url_base = 'music.andrewsamuelson.dev'
    features = [
        {'name': 'Active Listening', 'description': 'I have tried to implement a machine learning model that will look at your current playlist and try to override the random shuffling to create custom suggested track songs based on your active listening habits. This will work best with large playlists.', 'url': url_base + reverse('active-listening')},
    ]
    context.update({'features': features})
    return render(request, 'albums/experimental_list.html', context)

def get_sp_auth(page):
    if os.environ['ENVIRON_SETTING'] == 'dev':
        url_base = 'http://localhost:8000'
    else:
        url_base = 'music.andrewsamuelson.dev'

    redirect_uri = url_base + reverse(page)
    # spotipy.oauth2.SpotifyOAuth(os.environ['SPOTIFY_CLIENT_ID'], os.environ['SPOTIFY_CLIENT_SECRET'], redirect_uri, scope='')
    return oauth2.SpotifyOAuth( os.environ['SPOTIFY_CLIENT_ID'], os.environ['SPOTIFY_CLIENT_SECRET'], redirect_uri, scope='user-read-currently-playing')


def active_listening(request):
    setattr(spotipy.Spotify, 'current_user_playing_track', current_user_playing_track)
    print("REQUEST", request.path_info)
    context = {}
    access_token = ""

    sp_oauth = get_sp_auth('active-listening')
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = 'http://localhost:8000/' + request.get_full_path()
        print("URL", url)
        code = sp_oauth.parse_response_code(url)
        print("CODE", code)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        user = sp.current_user()
        method_list = [func for func in dir(sp) if callable(getattr(sp, func))]
        print("METHODS", method_list)
        # current_track = sp.next()
        current_track = sp.current_user_playing_track()
        #sp.current_track()
        #sp.currently_playing()
        #sp.current_playback()
        print("CURRENT", current_track)
        context.update({'user': user, 'current_track': current_track})
        return render(request, 'albums/active_listening.html', context)
    else:
        context = {'loginBtn': htmlForLoginButton()}
        return render(request, 'albums/active_listening.html', context)

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a class='btn btn-warning center' href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    sp_oauth = get_sp_auth('active-listening')
    auth_url = sp_oauth.get_authorize_url()
    return auth_url