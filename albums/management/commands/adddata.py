from django.core.management.base import BaseCommand, CommandError
from django.db.utils import DataError
from albums.models import Album

from urllib.request import urlopen
import urllib.parse
import urllib.request
from googlesearch import search
from bs4 import BeautifulSoup as bs
from time import sleep
import datetime as dt

import os, ssl, re



class Command(BaseCommand):
    help = 'Adds additional data that needs to be webscraped.'

    def handle(self, *args, **options):
        albums = Album.objects.exclude(name__icontains="?")
        albums = albums.exclude(artist__name__icontains="?")
        albums = albums.exclude(name="")
        for album in albums:
            print(album)
            scrape(album)


#grab the html for the page
def fetch_url(url):
    url = url.encode('ascii', errors="ignore").decode()
    html = urlopen(url)
    soup = bs(html, "html.parser")
    return soup


#### Helper functions
#### WIKIPEDIA HELPER FUNCTIONS
def find_urls(album):
    album_name = album.name
    artist_name = album.artist.name
    query = album_name + " " + artist_name

    urls = {'wiki' : None, 'bc' : None}

    for result in search(query, num=10, stop=10, pause=2):
        if 'wikipedia.org' in result:
            if 'song' not in result:
                if urls['wiki'] == None:
                    urls.update({'wiki' : result})
        if 'bandcamp.com' in result:
            if 'album' in result:
                if urls['bc'] == None:
                    urls.update({'bc' : result})
    
    query = query + " wikipedia bandcamp"
    for result in search(query, num=10, stop=10, pause=2):
        if 'wikipedia' in result:
            if urls['wiki'] == None:
                urls.update({'wiki' : result})
        if 'bandcamp' in result:
            urls.update({'bc' : result})
    
    return urls

#disambiguation check (multiple pages)
def wiki_artist_check(soup, album):
    description = soup.find('th', {'class':'description'})
    if description:
        if album.artist.name in description.getText():
            return True
        else:
            return False
    else:
        return False

def disambiguation_check(album):
    album_name = album.name.replace(" ", "_")
    url = "https://en.wikipedia.org/wiki/" + album_name + "_(disambiguation)"
    try:
        fetch_url(url)
    except(ValueError, urllib.error.HTTPError):
        #disambig exists
        url = "https://en.wikipedia.org/wiki/" + album_name
    return url

#double check for an album that shares a name with other albums (or things)
def wiki_double_named_album(url, album):
    try:
        soup = fetch_url(url)
    except(urllib.error.HTTPError):
        return url
    message = album.name + ' may refer to:'
    check = soup.find('div', {'class':'mw-parser-output'}).getText()
    url = "https://en.wikipedia.org/wiki/"
    album_name = album.name.replace(" ", "_")
    if message in check:
        artist_name = album.artist.name.replace(" ", "_")
        url += album_name + '_(' + artist_name + '_album)'
        return url
    else:
        return url + album_name
    
#finds the full length of the album
def wiki_full_length(soup):
    span = soup.find('span', {'class':'min'})
    if span:
        minutes = span.getText() 
        seconds = soup.find('span', {'class':'s'}).getText()
        total_time = dt.timedelta(minutes=int(minutes), seconds=int(seconds))
        return total_time
    else:
        return None

#clean the wiki release date before parsing
def wiki_clean_date(soup):
    for child in soup.find_all("span"):
        child.decompose()
    for child in soup.find_all("sup"):
        child.decompose()

#parse the date from wikipedia
def wiki_parse_date(unparsed_date):
    date_format = None
    #handles all possible date_strings (order of string is important)
    patterns = [
        {'re' : r'\d{1,2}\s\w{3,12}\s\d{4}', 'date_string' : '%d %B %Y'},
        {'re' : r'\w{3,12}\s\d{1,2}\s\d{4}', 'date_string' : '%B %d %Y'},
        {'re' : r'\w{3,12}\s\d{1,2}\S\s\d{4}', 'date_string' : '%B %d, %Y'},
        {'re' : r'\w{3,12}\s\d{4}', 'date_string' : '%B %Y'},
        {'re' : r'\d{4}', 'date_string' : '%Y'}
    ]

    for pattern in patterns:
        match = re.search(pattern['re'], unparsed_date)
        if match:
            date_format = pattern['date_string']
            break
    if date_format:
        try:
            return dt.datetime.strptime(match.group(0), date_format)
        except(ValueError):
            print("Problem with " + match.group(0))
            return None
    else:
        print('Unrecognized pattern: ' + unparsed_date)
        return None

#finds the release date of the album
def wiki_release_date(soup):
    span = soup.find('td', {'class':'published'})
    if span:
        wiki_clean_date(span)
        unparsed_date = span.getText().strip('\n')
        if unparsed_date == '':
            return None
        else:
            released = wiki_parse_date(unparsed_date)
        # try:
        #     released = dt.datetime.strptime(unparsed_date, '%d %B %Y')
        # except(ValueError):
        #     try:
        #         released = dt.datetime.strptime(unparsed_date, '%B %d, %Y')
        #     except(ValueError):
        #         return None
        return released
    else:
        return None

#finds the album art from wikipedia
def wiki_album_art(soup):
    sidebar = soup.find('table', {'class': 'infobox vevent haudio'})
    if sidebar:
        try:
            img = sidebar.find('img')['src']
            return img
        except(TypeError):
            return None
    return None


#### BANDCAMP HELPER FUNCTIONS
#helps filter if weird characters
def filter_str(string):
    return string.encode('ascii', errors="ignore").decode().replace(" ", "")

#loop through pages search results for proper url; returns nothing if match not found
def search_results(results_list, album, search_term):
    album_artist = album.artist.name.lower()
    album_name = album.name.lower()
    for item in results_list:
        if item.find('div', {'class':'itemtype'}).getText().strip() == search_term:
            album = item.find('div', {'class':'heading'}).getText().lower().strip()
            artist = item.find('div', {'class':'subhead'}).getText().lower().strip()[3:]
            url = item.find('a', {'class':'artcont'})['href']
            if (filter_str(artist) == filter_str(album_artist)) and (filter_str(album) == filter_str(album_name)):
                end = url.find("?")
                return url[:end]
    return ""

#check for album
def check_album(album):
    num = 1
    while num <= 5:
        url = 'https://bandcamp.com/search?page=' + str(num) + '&q=' + album.name.replace(" ", "%20")
        try:
            html = fetch_url(url)
        except(urllib.error.HTTPError):
            return None
        search_term = "ALBUM"
        left_div = html.find('ul', {'class', 'result-items'})
        list_items = left_div.findAll('li')   
        album_url = search_results(list_items, album, search_term)
        if album_url:
            return album_url
        else:
            num += 1
    return None

#check for artist instead of album
def check_artist(album):
    num = 1
    while num <= 5:
        url = 'https://bandcamp.com/search?page=' + str(num) + '&q=' + album.artist.name.replace(" ", "%20")
        if url == 'https://bandcamp.com/search?q=':
            return None
        html = fetch_url(url)
        search_term = "ALBUM"
        left_div = html.find('ul', {'class', 'result-items'})
        list_items = left_div.findAll('li')
        album_url = search_results(list_items, album, search_term)
        if album_url:
            return album_url
        else:
            num += 1

#find a search result on bandcamp that matches
def bc_navigate_to_page(album):
    url = check_album(album)
    if not url:
        url = check_artist(album)
        if not url:
            return "skip"
        else:
            return url
    else:
        return url        

#find the length of the album on bandcamp    
def bc_full_length(soup):
    times = soup.findAll('span', {'class':'time secondaryText'})
    lengths = []
    pass
    for time in times:
        time = time.getText().strip()
        lengths.append(time)
    total_length = dt.timedelta()
    for i in lengths:
        (m, s) = i.split(':')
        d = dt.timedelta(minutes=int(m), seconds=int(s))
        total_length += d
    return total_length

#find the release date of the album on bandcamp
def bc_release_date(soup):
    init_div = soup.find('div', {'class':'tralbumData tralbum-credits'})
    if init_div:
        unparsed_date = init_div.find('meta')['content']
        if unparsed_date:
            release_date = dt.datetime.strptime(unparsed_date, '%Y%m%d')
            return release_date
    else:
        return None

def bc_album_art(soup):
    div = soup.find('div', {'id': 'tralbumArt'})
    if div:
        img = div.find('img')['src']
        if img:
            return img
    return None   

#### main functions

#check wikipedia for the album
def scrape_wiki(album):
    try:
        html = fetch_url(album.wiki_url)
    except(ValueError, urllib.error.HTTPError):
        #print("Couldn't find Wikipedia page")
        return
    # if wiki_artist_check(html, album):
    if not album.time_check():
        album.time_length = wiki_full_length(html)
    
    if not album.release_date_check():
        album.release_date = wiki_release_date(html)
    
    if not album.album_art_check():
        album.album_art = wiki_album_art(html)
    album.save()
    return
        
def scrape_bc(album):
    if not album.bc_url:
        try:
            url = bc_navigate_to_page(album)
        except(urllib.error.HTTPError):
            return
    else:
        url = album.bc_url
    if url == "skip":
        return
    try:
        html = fetch_url(url)
    except(ValueError, urllib.error.HTTPError):
        print("Couldn't find bandcamp page")
        return

    if not album.time_check():
        album.time_length = bc_full_length(html)
    
    if not album.release_date_check():
        album.release_date = bc_release_date(html)

    if not album.album_art_check():
        album.album_art = bc_album_art(html)
    album.save()

    return
        
def scrape(album):
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)): 
        ssl._create_default_https_context = ssl._create_unverified_context
    if album.all_info_found():
        return

    if album.has_url():
        if album.wiki_url:
            scrape_wiki(album)
    else:
        sleep(5)
        urls = find_urls(album)
        if urls['wiki']:
            album.wiki_url = urls['wiki']
        if urls['bc']:
            album.bc_url = urls['bc']
        try:
            album.save()
        except(DataError):
            album.album_art = None
            album.save()
        
        if album.wiki_url:
            scrape_wiki(album)


    if album.all_info_found():
        return
    else:
        # print("Checking Bandcamp")
        scrape_bc(album)


    if not album.time_check():
        print("Unable to find total length of album")
    if not album.release_date_check():
        print("Unable to find album publish date")
    if not album.album_art_check():
        print("Unable to find album art")