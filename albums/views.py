from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from albums.models import *
from albums.forms import AlbumForm, ReccForm

from .management.commands.scrape import scrape

import datetime as dt

# Create your views here.
def main(request):
    context = {}
    albums = Album.objects.exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    
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
    albums = Album.objects.filter(artist__slug=artist).order_by('release_date')
    artist = Artist.objects.filter(slug=artist).first()
    context = {
        'albums' : albums,
        'artist' : artist
    }
    return render(request, 'albums/artist_page.html', context)

def statistics(request):
    #albums not in queue
    albums = Album.objects.exclude(date_finished=None)
    
    #albums in queue
    queue = Album.objects.filter(date_finished=None)

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
    total_time = format_sum_time(total_time)


    #count the number of albums listened in each primary genre
    genre_count = []
    for genre in PrimaryGenre.objects.all():
        count = albums.filter(primary_genre=genre).count()
        genre_count.append({'genre' : genre, 'count': count})
    
    #gather the queue length
    queue_length = queue.count()

    #gather length of queue
    queue_time = dt.timedelta(seconds=0)
    for album in queue:
        if album.time_length:
            queue_time += album.time_length
    queue_time = format_sum_time(queue_time)

    


    #collect all the statistics
    context.update({
        'total_album_num' : total_album_num,
        'total_subgenres_num' : total_subgenres_num,
        'total_time' : total_time,
        'genre_count' : genre_count,
        'queue_length' : queue_length,
        'queue_time' : queue_time
    })

    return render(request, 'albums/statistics.html', context)

def primary_genre(request, genre):
    primary_genre = PrimaryGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(primary_genre=primary_genre).exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'genre' : primary_genre, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/primary_genre.html', context)

def secondary_genre(request,genre):
    sub_genre = SubGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(subgenres__subgenre__name__iexact=genre).exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'genre' : sub_genre, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/subgenre.html', context)

def group(request, group):
    if group == "queue":
        albums = Album.objects.filter(date_finished=None).order_by('order')
    elif group == "vinyl":
        albums = Album.objects.filter(vinyl=True).order_by('order')
    elif group == "cassette":
        albums = Album.objects.filter(cassette=True).order_by('order')
    else:
        albums = Album.objects.filter(groups__group__name__iexact=group)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'group' : group, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/groups.html', context)

def chart_landing(request):
    num_of_charts = Album.objects.all().order_by('-chart').first().chart
    nums = range(1, num_of_charts)
    context = {'charts': nums}
    return render(request, 'albums/landing/chart.html', context)

def chart(request, chart_num):
    albums = Album.objects.filter(chart=chart_num).order_by('order')
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'chart_num' : chart_num, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/charts.html', context)

def suggest(request):
    if request.POST:
        form = ReccForm(request.POST)
        if form.is_valid():
            Recommendation.objects.create(
                recommender = form.cleaned_data['recc_name'],
                album_name = form.cleaned_data['album_name'],
                artist_name = form.cleaned_data['artist_name'],
                genre = form.cleaned_data['genre'],
                url = form.cleaned_data['url'],
                note = form.cleaned_data['note']
            )
            context = {
                'album' : form.cleaned_data['album_name']
            }
            return render(request, 'albums/thanks.html', context)
    else:
        form = ReccForm()
        context = {'form': form}
        return render(request, 'albums/suggestion.html', context)

def about(request):
    return render(request, 'albums/about.html')

@login_required
def edit_album(request, artist, album):
    album = Album.objects.filter(slug=album, artist__slug=artist).first()
    saved = None
    error = None
    if request.POST:
        form = AlbumForm(request.POST)
        if form.is_valid():
            album.name = form.cleaned_data['name']
            album.artist = form.cleaned_data['artist']
            album.date_finished = form.cleaned_data['date_finished']
            album.primary_genre = form.cleaned_data['primary_genre']
            album.wiki_url = form.cleaned_data['wiki_url']
            album.bc_url = form.cleaned_data['bc_url']
            album.amazon_url = form.cleaned_data['amazon_url']
            album.time_length = form.cleaned_data['time_length']
            album.release_date = form.cleaned_data['release_date']
            album.album_art = form.cleaned_data['album_art']
            album.vinyl = form.cleaned_data['vinyl']
            album.cassette = form.cleaned_data['cassette']

            if form.cleaned_data['subgenres']:
                subgenres = form.cleaned_data['subgenres'].split('/')
                for genre in subgenres:
                    genre_inst = SubGenre.objects.filter(name__iexact=genre).first()

                    if not genre_inst:
                        genre_inst = SubGenre.objects.create(name=genre)

                    AlbumSubgenre.objects.create(
                            album = album,
                            subgenre = genre_inst
                        )

            if form.cleaned_data['rating']:
                last_rating = Rating.objects.filter(album=album).first()
                if last_rating:
                    last_rating = last_rating.listen
                else:
                    last_rating = 0
                    
                Rating.objects.create(
                    album=album,
                    score=form.cleaned_data['rating'],
                    listen = last_rating + 1
                )
            
            album.save()

            saved = True
        else:
            error = True


    form = AlbumForm(instance=album)

    context = {'form': form, 'album': album, 'saved': saved, 'error': error}
    return render(request, 'albums/edit_album.html', context)

@login_required
def add_album(request):
    saved = None
    error = None
    if request.POST:
        form = AlbumForm(request.POST)

        if form.is_valid():
            if request.POST.get('new_artist'):
                artist = Artist.objects.filter(name__iexact=request.POST.get('new_artist')).first()
                if not artist:
                    artist = Artist.objects.create(name=request.POST.get('new_artist'))
            else:
                artist = form.cleaned_data['artist']

            album = Album.objects.create(
                name = form.cleaned_data['name'],
                artist = artist,
                date_finished = form.cleaned_data['date_finished'],
                primary_genre = form.cleaned_data['primary_genre'],
                wiki_url = form.cleaned_data['wiki_url'],
                bc_url = form.cleaned_data['bc_url'],
                amazon_url = form.cleaned_data['amazon_url'],
                time_length = form.cleaned_data['time_length'],
                release_date = form.cleaned_data['release_date'],
                album_art = form.cleaned_data['album_art'],
                vinyl = form.cleaned_data['vinyl'],
                cassette = form.cleaned_data['cassette']
            )

            if form.cleaned_data['subgenres']:
                subgenres = form.cleaned_data['subgenres'].split('/')
                for genre in subgenres:
                    genre_inst = SubGenre.objects.filter(name__iexact=genre).first()

                    if not genre_inst:
                        genre_inst = SubGenre.objects.create(name=genre)

                    AlbumSubgenre.objects.create(
                            album = album,
                            subgenre = genre_inst
                        )

            if form.cleaned_data['rating']:
                last_rating = Rating.objects.filter(album=album).first()
                if last_rating:
                    last_rating = last_rating.listen
                else:
                    last_rating = 0

                Rating.objects.create(
                    album=album,
                    score=form.cleaned_data['rating'],
                    listen = last_rating + 1
                )

            scrape(album)

            saved = True
        else:
            error = True
    form = AlbumForm()

    context = {'saved': saved, 'error': error, 'form': form}
    return render(request, 'albums/add_album.html', context)
    

def htmltest(request):
    album = Album.objects.all().first()
    form = AlbumForm(instance=album)

    context = {'form': form, 'album': album}
    return render(request, 'albums/test.html', context)


########## NON-RENDER FUNCTIONS ###########
def search_albums(request, albums):
    if request:
        search = request.get('search')
        order_post = request.get('order')
        direction = request.get('direction')

        if search == None:
            search == ''

        add = ""
        if direction == "down":
            add = "-"

        if order_post:
            orders = {
                'name' : 'name',
                'artist' : 'artist__name',
                'time' : 'time_length',
                'listen_date' : 'date_finished',
                'rating' : 'current_rating',
                'release' : 'release_date'
            }

            order_term = add + orders[order_post]

            print(order_term)
            if order_term == 'date_finished':
                albums = albums.order_by(order_term, add + 'order')
            else:
                albums = albums.order_by(order_term)
    else:
        search = ''
        order_post = ''
        direction = 'up'
    return albums, search, order_post, direction

#takes a time delta and nicely formats to a string
def format_sum_time(sum_time):
    hours, remainder = divmod(sum_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if sum_time.days:
        return '{:02}d {:02}h {:02}m {:02}s'.format(int(sum_time.days), int(hours), int(minutes), int(seconds))
    else:
        return '{:02}h {:02}m {:02}s'.format(int(hours), int(minutes), int(seconds))