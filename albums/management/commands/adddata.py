from django.core.management.base import BaseCommand, CommandError
from albums.models import Album

from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup as bs
import datetime as dt

class Command(BaseCommand):
    help = 'Reads in data from the initial spreadsheet.'

    def handle(self, *args, **options):
        albums = Album.objects.all()
        for album in albums:
            scrape(album)


#grab the html for the page
def fetch_url(url):
    url = url.encode('ascii', errors="ignore").decode()
    html = urlopen(url)
    soup = bs(html, "html.parser")
    return soup


#### Helper functions
#### WIKIPEDIA HELPER FUNCTIONS
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
        return ""

#clean the wiki release date before parsing
def wiki_clean_date(soup):
    for child in soup.find_all("span"):
        child.decompose()
    for child in soup.find_all("sup"):
        child.decompose()

#finds the release date of the album
def wiki_release_date(soup):
    span = soup.find('td', {'class':'published'})
    if span:
        wiki_clean_date(span)
        unparsed_date = span.getText().strip('\n')
        try:
            released = dt.datetime.strptime(unparsed_date, '%d %B %Y')
        except(ValueError):
            released = dt.datetime.strptime(unparsed_date, '%B %d, %Y')
        return released
    else:
        return ""

#finds the album art from wikipedia
def wiki_album_art(soup):
    sidebar = soup.find('table', {'class': 'infobox vevent haudio'})
    if sidebar:
        img = sidebar.find('img')['src']
        if img:
            return img
    return ""


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
        html = fetch_url(url)
        search_term = "ALBUM"
        left_div = html.find('ul', {'class', 'result-items'})
        list_items = left_div.findAll('li')   
        album_url = search_results(list_items, album, search_term)
        if album_url:
            return album_url
        else:
            num += 1
    return ""

#check for artist instead of album
def check_artist(album):
    num = 1
    while num <= 5:
        url = 'https://bandcamp.com/search?page=' + str(num) + '&q=' + album.artist.name.replace(" ", "%20")
        if url == 'https://bandcamp.com/search?q=':
            return
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
    unparsed_date = init_div.find('meta')['content']
    release_date = dt.datetime.strptime(unparsed_date, '%Y%m%d')
    return release_date

def bc_album_art(soup):
    div = soup.find('div', {'id': 'tralbumArt'})
    if div:
        img = div.find('img')['src']
        if img:
            return img
    return ""    

#### main functions

#check wikipedia for the album
def scrape_wiki(album):
    url = disambiguation_check(album)
    url = wiki_double_named_album(url, album)
    try:
        html = fetch_url(url)
    except(ValueError, urllib.error.HTTPError):
        #print("Couldn't find Wikipedia page")
        return
    if wiki_artist_check(html, album):

        if album.time_check():
            album.time = wiki_full_length(html)
        
        if album.release_date_check():
            album.release_date = wiki_release_date(html)
        
        if album.album_art_check():
            album.album_art = wiki_album_art(html)
    
    return
        
def scrape_bc(album):
    url = bc_navigate_to_page(album)
    if url == "skip":
        return
    try:
        html = fetch_url(url)
    except(ValueError):
        print("Couldn't find bandcamp page")
        return

    if album.time_check():
        album.time_length = bc_full_length(html)
    
    if album.release_date_check():
        album.release_date = bc_release_date(html)

    if album.album_art_check():
        album.album_art = bc_album_art(html)
    
    return album_object
        
def scrape(album):
    # print("Checking Wikipedia")
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