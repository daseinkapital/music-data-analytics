from django.shortcuts import render
from albums.models import *
from django.db.models import Q

import datetime as dt

# Create your views here.
def main(request):
    context = {}
    if request.POST:
        search = request.POST.get('search')
        order_post = request.POST.get('order')
        direction = request.POST.get('direction')
    else:
        search = ''
        order_post = ''
        direction = 'up'

    if search == None:
        search == ''

    if direction == "down":
        add = "-"
    else:
        add = ""

    if order_post:
        orders = {
            'name' : 'name',
            'artist' : 'artist__name',
            'time' : 'time_length',
            'listen_date' : 'date_finished',
            'rating' : 'rating',
            'release' : 'release_date'
        }

        order_term = orders[order_post]

        if order_term == 'rating':
            albums = Album.objects.all()
        elif order_term == 'date_finished':
            albums = Album.objects.all().order_by(add+order_term, add+'order')
        else:
            albums = Album.objects.all().order_by(add + order_term)
    
    else:
        albums = Album.objects.all().order_by(add + 'name')
    
    context.update({'albums': albums})
    context.update({
        'search' : search,
        'order' : order_post,
        'direction' : direction
    })
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

    return render(request, 'albums/statistics.html', context)

def about(request):
    return render(request, 'albums/about.html')

def htmltest(request):
    return render(request, 'albums/test.html')

def search(request):
    term = request.GET.get('term')
    print("Term: " + term)
    if term:
        albums = Album.objects.filter(Q(name__iexact=term) | Q(artist__name__iexact=term))
    return albums