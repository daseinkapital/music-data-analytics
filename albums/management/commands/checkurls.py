from django.core.management.base import BaseCommand, CommandError
from albums.models import Album, ListenURL

from urllib.request import urlopen
import urllib.parse
import urllib.request
from googlesearch import search

from bs4 import BeautifulSoup as bs
from time import sleep
import datetime as dt

from .scrape import fetch_url, bc_navigate_to_page, screw_the_rules

class Command(BaseCommand):
    help = 'Reads in data from the old albums list.'

    def handle(self, *args, **options):
        screw_the_rules()
        albums = Album.objects.all()
        for album in albums:
            print(album)
            check_urls(album)

def check_urls(album):
    listen_url = ListenURL.objects.filter(album=album).first()

    if not listen_url:
        print('Problem with listen URLs')
        return

    missing_urls = find_missing_urls(album)

    if not album.bc_url:
        bc_url = find_bandcamp(album)
        if bc_url == "skip":
            bc_url = None
        if bc_url:
            album.bc_url = bc_url
            print('Bandcamp URL found for {0}'.format(album))

    if missing_urls == []:
        return

    urls = {}

    for site in missing_urls:
        urls.update({site : find_url(album, site)})
    
    for site in missing_urls:
        if site == 'wikipedia.org':
            if urls[site] != None:
                album.wiki_url = urls[site]
                print('Wikipedia URL found for {0}'.format(album))
        if site == 'amazon.com':
            if urls[site] != None:
                album.amazon_url = urls[site]
                print('Amazon URL found for {0}'.format(album))
        if site == 'discogs.com':
            if urls[site] != None:
                album.discogs_url = urls[site]
                print('Discogs URL found for {0}'.format(album))
        if site == 'spotify.com':
            if urls[site] != None:
                listen_url.spotify = urls[site]
                print('Spotify URL found for {0}'.format(album))
        if site == 'itunes.apple.com':
            if urls[site] != None:
                listen_url.itunes = urls[site]
                print('iTunes URL found for {0}'.format(album))

    album.save()
    listen_url.save()

    return
        

    


def find_missing_urls(album):
    missing_urls = [
        'wikipedia.org',
        'amazon.com',
        'discogs.com',
        'itunes.apple.com',
        'spotify.com'
    ]

    if album.wiki_url:
        missing_urls.remove('wikipedia.org')
    if album.amazon_url:
        missing_urls.remove('amazon.com')
    if album.discogs_url:
        missing_urls.remove('discogs.com')
    if album.has_spotify():
        missing_urls.remove('spotify.com')
    if album.has_itunes():
        missing_urls.remove('itunes.apple.com')
    
    return missing_urls

def find_url(album, site):
    album_name = album.name
    artist_name = album.artist.name
    site_name = site.split('.')[0]
    if 'itunes' in site:
        site_name = 'itunes'

    query = "{0} {1} {2}".format(album_name, artist_name, site_name)

    site_url = None

    for result in search(query, num=10, stop=10, pause=3):
        if site in result:
            site_url = result
            break
    
    return site_url

def find_bandcamp(album):
    return bc_navigate_to_page(album)