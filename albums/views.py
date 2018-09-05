from django.shortcuts import render
from albums.models import *

import datetime as dt

# Create your views here.
def main(request):
    print("Hello")
    context = {}
    albums = Album.objects.all()
    context.update({'albums': albums})
    return render(request, 'albums/main.html', context)

def album_page(request, artist, album):
    album = Album.objects.filter(slug=album).filter(artist__slug=artist).first()
    context = {'album' : album}
    return render(request, 'albums/album_page.html', context)

def artist_page(request, artist):
    albums = Album.objects.filter(artist__slug=artist)
    artist = Artist.objects.filter(slug=artist).first()
    context = {
        'albums' : albums,
        'artist' : artist
    }
    return render(request, 'albums/artist_page.html', context)

def statistics(request):
    albums = Album.objects.all()
    total_subgenres_num = SubGenre.objects.all().count()
    total_album_num = albums.count()
    total_time = dt.timedelta(seconds=0)
    for album in albums:
        if album.time_length:
            total_time += album.time_length
    
    context = {
        'total_album_num' : total_album_num,
        'total_subgenres_num' : total_subgenres_num,
        'total_time' : total_time
    }
    print(context)

    return render(request, 'albums/statistics.html', context)

def about(request):
    return render(request, 'albums/about.html')

def htmltest(request):
    return render(request, 'albums/test.html')