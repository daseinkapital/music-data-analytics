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
    context = {}

    #count how many subgenres listened to
    total_subgenres_num = SubGenre.objects.all().count()

    #count the total number of albums
    total_album_num = albums.count()

    #determine the total amount of time of all albums (that have time data)
    total_time = dt.timedelta(seconds=0)
    for album in albums:
        if album.time_length:
            total_time += album.time_length

    #count the number of albums listened in each primary genre
    genre_count = []
    for genre in PrimaryGenre.objects.all():
        count = Album.objects.filter(primary_genre=genre).count()
        genre_count.append({'genre' : genre, 'count': count})


    #collect all the statistics
    context.update({
        'total_album_num' : total_album_num,
        'total_subgenres_num' : total_subgenres_num,
        'total_time' : total_time,
        'genre_count' : genre_count
    })

    return render(request, 'albums/statistics.html', context)

def primary_genre(request, genre):
    primary_genre = PrimaryGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(primary_genre=primary_genre)
    context = {'genre' : primary_genre, 'albums' : albums}
    return render(request, 'albums/primarygenre.html', context)

def secondary_genre(request,genre):
    sub_genre = SubGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(subgenres__subgenre__name_iexact=genre)
    context = {'genre' : sub_genre, 'albums' : albums}
    return render(request, 'albums/subgenre.html', context)

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