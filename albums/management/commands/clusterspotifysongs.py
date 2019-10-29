from django.core.management.base import BaseCommand, CommandError
from .getallalbumplaylists import write_to_json, read_from_json

import urllib.parse
import urllib.request
import spotipy
import spotipy.util as util

import os

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from math import sqrt

class Command(BaseCommand):
    help = "Uses clustering algorithms to try and create new playlists for users"

    def handle(self, *args, **options):
        filename = 'saved_track_analysis'
        print("Grabbing tracks")
        tracks = read_from_json(filename)
        if not tracks:
            tracks = get_all_saved_songs()
            print("Writing to {}".format(filename))
            write_to_json(tracks, filename)
        df = pd.DataFrame(tracks)
        print(df)
        non_data_cols = ['id', 'song_name', 'album_artist']
        info_data = df[non_data_cols]
        num_data = df[list(set(df.columns.tolist()) - set(non_data_cols))]
        clusters, groups = cluster(num_data)
        matched_playlists = df.assign(playlist = clusters)
        playlists = generate_playlists(matched_playlists, groups)
        for playlist in playlists:
            print(playlist)


def get_all_saved_songs(spotify_session=None):
    if not spotify_session:
        sp = init_spotify_creds()
    else:
        sp = spotify_session
    
    if sp:
        user_saved_tracks = []
        tracks = sp.current_user_saved_tracks(limit=50)
        while tracks:
            for track in tracks['items']:
                audio_features = sp.audio_features(tracks=[track['track']['id']])
                track_info = {
                    'id': track['track']['id'],
                    'song_name': track['track']['name'],
                    'album_artist': track['track']['artists'][0]['name'],
                    'danceability': audio_features[0]['danceability'],
                    'energy': audio_features[0]['energy'],
                    'key': audio_features[0]['key'],
                    'loudness': audio_features[0]['loudness'],
                    'mode': audio_features[0]['mode'],
                    'speechiness': audio_features[0]['speechiness'],
                    'acousticness': audio_features[0]['acousticness'],
                    'instrumentalness': audio_features[0]['instrumentalness'],
                    'liveness': audio_features[0]['liveness'],
                    'valence': audio_features[0]['valence'],
                    'tempo': audio_features[0]['tempo']
                }
                user_saved_tracks.append(track_info)
            tracks = sp.next(tracks)
    return user_saved_tracks

def normalize_column(data_col):
    data_col = (data_col - min(data_col))/(max(data_col) - min(data_col))
    return data_col

def generate_distance_matrix(data):
    d_mat = []
    names = data.columns.tolist()
    for index1, row1 in data.iterrows():
        print("index1", index1)
        row_distances = []
        for index2, row2 in data.iterrows():
            if index1 < index2:
                total = 0
                for name in names:
                    total += (row1[name] - row2[name])**2
                row_distances.append(sqrt(total))
            else:
                row_distances.append(0)
        d_mat.append(row_distances)
    for i in range(len(d_mat[0])):
        for j in range(i, len(d_mat[0])):
            d_mat[j][i] = d_mat[i][j]
    return np.array(d_mat)

def cluster(num_data):
    for name in num_data.columns.tolist():
        num_data[name] = normalize_column(num_data[name])

    d_mat = generate_distance_matrix(num_data)


    clusters = DBSCAN(eps=3.15).fit_predict(d_mat)
    groups = list(set(clusters))
    groups.pop(-1)
    return clusters, groups

def generate_playlists(full_data, groups):
    playlists = []
    for i in full_data:
        playlists.append(full_data[full_data['playlist']==i])
    return playlists

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