from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from albums.models import *
from albums.forms import AlbumForm, ReccForm, consolidateSubgenreForm
from albums.functions.stats import *

from .management.commands.scrape import scrape
from .management.commands.checkurls import check_urls
from .management.commands.updatealbumart import update_art

import datetime as dt

import random


# Create your views here.
def main(request):
    context = {}
    albums = Album.objects.exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    
    context.update({'albums': albums})
    context.update({
        'search' : search,
        'order' : order_post,
        'direction' : direction,
        'home' : 'active'
    })
    return render(request, 'albums/renders/main.html', context)

def album_page(request, artist, album):
    album = Album.objects.filter(slug=album).filter(artist__slug=artist).first()
    album_has_url = album.has_url()
    context = {'album' : album, 'has_url' : album_has_url}
    print(context)
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

    #count the total number of albums
    total_album_num = albums.count()

    #average rating of all albums
    total_avg_rating = average_rating(albums)

    #average new music per day since start
    avg_new_music = average_listen_time_per_day(albums)
    
    #count how many subgenres listened to
    total_subgenres_num = SubGenre.objects.all().count()

    #determine the total amount of time of all albums (that have time data)
    total_time = time_total(albums)

    #count the number of albums listened in each primary genre
    genre_count = generate_genre_table(albums)
    
    #gather the queue length
    queue_length = queue.count()

    #gather length of queue
    queue_time = time_total(queue)

    #estimated queue completion time
    queue_completion = queue_completion_time(albums, queue)


    #collect all the statistics
    context.update({
        'total_album_num' : total_album_num,
        'total_avg_rating' : total_avg_rating,
        'avg_new_music' : avg_new_music,
        'total_subgenres_num' : total_subgenres_num,
        'total_time' : total_time,
        'genre_count' : genre_count,
        'queue_length' : queue_length,
        'queue_time' : queue_time,
        'queue_completion' : queue_completion,
        'stat' : 'active'
    })

    return render(request, 'albums/statistics.html', context)

def primary_genre(request, genre):
    primary_genre = PrimaryGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(primary_genre=primary_genre).exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'genre' : primary_genre, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/renders/primary_genre.html', context)

def prime_genre_landing(request):
    genres = PrimaryGenre.objects.all()
    context = {'genres' : genres}
    return render(request, 'albums/landing/primary_genre.html', context)

def secondary_genre(request,genre):
    sub_genre = SubGenre.objects.filter(name__iexact=genre).first()
    albums = Album.objects.filter(subgenres__subgenre__name__iexact=genre).exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'genre' : sub_genre, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/renders/subgenre.html', context)

def subgenre_landing(request):
    genres = SubGenre.objects.all()
    context = {'genres' : genres}
    return render(request, 'albums/landing/subgenre.html', context)

@login_required
def consolidate_subgenre(request):
    context = {}
    if request.POST:
        form = consolidateSubgenreForm(request.POST)
        if form.is_valid():
            good_subgenre = form.cleaned_data['official_subgenre']
            bad_subgenre = form.cleaned_data['mismatched_subgenre']
            bad_subgenre_album = AlbumSubgenre.objects.filter(subgenre=bad_subgenre)
            for album in bad_subgenre_album:
                album.subgenre = good_subgenre
                album.save()
            bad_subgenre_album = AlbumSubgenre.objects.filter(subgenre=bad_subgenre)
            if bad_subgenre_album.count() == 0:
                bad_subgenre.delete()
            
            good_name = good_subgenre.name
            bad_name = bad_subgenre.name

            context.update({'good_name' : good_name, 'bad_name' : bad_name, 'form' : form})
    else:
        context.update({'form': consolidateSubgenreForm()})
    
    return render(request, 'albums/consolidate_subgenre.html', context)
                

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
    return render(request, 'albums/renders/groups.html', context)

def chart_landing(request):
    num_of_charts = Album.objects.all().order_by('-chart').first().chart
    nums = range(num_of_charts)
    context = {'charts': nums}
    return render(request, 'albums/landing/chart.html', context)

def chart(request, chart_num):
    albums = Album.objects.filter(chart=chart_num).order_by('order')
    albums, search, order_post, direction = search_albums(request.POST, albums)
    context = {'chart_num' : chart_num, 'albums' : albums}
    context.update({'search' : search, 'order' : order_post, 'direction' : direction})
    return render(request, 'albums/renders/charts.html', context)

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
                amazon_referral_url = form.cleaned_data['amazon_referral_url'],
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

def match_game(request):
    print(request.POST)
    context = {}

    if request.POST:
        answer = request.POST.get('answer')
        selected = request.POST.get('selected')
        attempts = int(request.POST.get('attempts'))
        correct = int(request.POST.get('correct'))
        if request.POST.get('total-points'):
            point_total = int(request.POST.get('total-points'))
            points = int(request.POST.get('points'))
        else:
            point_total = 0
            points = 0

        if answer:
            if answer == selected:
                correct += 1
                point_total += points
            else:
                point_total -= points
        
        albums = Album.objects.exclude(album_art=None)
        album_count = albums.count()
        choices = generate_choices(album_count)
        answer_num = random_num(3)
        choice_dict = {
            0 : 'A',
            1 : 'B',
            2 : 'C',
            3 : 'D'
        }
        answer_letter = choice_dict[answer_num]
        answer = {'num' : answer_num, 'letter' : answer_letter}
        album_display = choices[answer_num]['album']
        percent_correct = 100
        if attempts != 0:
            percent_correct = round((correct/attempts)*100)
        attempts += 1
        context.update({
            'choices' : choices,
            'album_display' : album_display,
            'attempts' : attempts,
            'correct' : correct,
            'answer' : answer,
            'percent' : percent_correct,
            'point_total': point_total
        })
        return render(request, 'albums/game/round.html', context)
    
    return render(request, 'albums/game/main.html')

def about(request):
    context = {'about' : 'active'}
    return render(request, 'albums/about.html', context)


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
            album.discogs_url = form.cleaned_data['discogs_url']
            album.itunes_url = form.cleaned_data['itunes_url']
            album.soundcloud_url = form.cleaned_data['soundcloud_url']
            album.spotify_url = form.cleaned_data['spotify_url']
            album.youtube_url = form.cleaned_data['youtube_url']
            album.time_length = form.cleaned_data['time_length']
            album.release_date = form.cleaned_data['release_date']
            album.album_art = form.cleaned_data['album_art']
            album.vinyl = form.cleaned_data['vinyl']
            album.cassette = form.cleaned_data['cassette']
            album.personally_checked = form.cleaned_data['personally_checked']
            album.note = form.cleaned_data['note']

            if form.cleaned_data['subgenres']:
                subgenres = form.cleaned_data['subgenres'].split(',')
                for genre in subgenres:
                    genre_inst = SubGenre.objects.filter(name__iexact=genre.strip()).first()

                    if not genre_inst:
                        genre_inst = SubGenre.objects.create(name=genre.strip())

                    subgenre_assign = AlbumSubgenre.objects.filter(album=album, subgenre=genre_inst).first()

                    if not subgenre_assign: 
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
            if not AlbumArtist.objects.filter(artist=form.cleaned_data['artist'], album=album).first():
                AlbumArtist.objects.create(
                    album=album,
                    artist=artist
                )
            
            album.save()
            if not album.personally_checked:
                check_urls(album)
            if 'upload' in album.album_art:
                update_art(album)

            saved = True
            form = AlbumForm(instance=album)

            context = {'form': form, 'album': album, 'saved': saved, 'error': error}
            return render(request, 'albums/edit_album.html', context)
        else:
            error = True
            form = AlbumForm(instance=album, initial={'date_finished':request.POST.get('date_finished'),'rating':request.POST.get('rating'),'subgenres':request.POST.get('subgenres')})
            context = {'form': form, 'album': album, 'saved': saved, 'error': error}
            return render(request, 'albums/edit_album.html', context)

    form = AlbumForm(instance=album)
    for whatever in form:
        print(whatever.label_tag())
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
                discogs_url = form.cleaned_data['discogs_url'],
                itunes_url = form.cleaned_data['itunes_url'],
                spotify_url = form.cleaned_data['spotify_url'],
                soundcloud_url = form.cleaned_data['soundcloud_url'],
                youtube_url = form.cleaned_data['youtube_url'],
                time_length = form.cleaned_data['time_length'],
                release_date = form.cleaned_data['release_date'],
                album_art = form.cleaned_data['album_art'],
                vinyl = form.cleaned_data['vinyl'],
                cassette = form.cleaned_data['cassette'],
                note = form.cleaned_data['note']
            )

            if form.cleaned_data['subgenres']:
                subgenres = form.cleaned_data['subgenres'].split(',')
                for genre in subgenres:
                    genre_inst = SubGenre.objects.filter(name__iexact=genre.strip()).first()

                    if not genre_inst:
                        genre_inst = SubGenre.objects.create(name=genre.strip())

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

            AlbumArtist.objects.create(
                album=album,
                artist=artist
            )

            saved = True
        else:
            error = True
            form = AlbumForm(instance=album, initial={'date_finished':request.POST.get('date_finished'),'rating':request.POST.get('rating'),'subgenres':request.POST.get('subgenres')})
            context = {'saved': saved, 'error': error, 'form': form}
            return render(request, 'albums/add_album.html', context)
    form = AlbumForm()

    context = {'saved': saved, 'error': error, 'form': form}
    return render(request, 'albums/add_album.html', context)

@login_required
def issue_manager(request):
    open_issues = ReportIssue.objects.exclude(resolved=True)
    context = {'issues' : open_issues}
    return render(request, 'albums/open_issues.html', context)

def page_not_found(request):
    return render(request, '404.html')

def internal_server_error(request):
    return render(request, '404.html')

@login_required
def recommendations(request):
    reccs = Recommendation.objects.filter(accepted=False)
    context = {'reccs' : reccs}
    return render(request, 'albums/recommendation_review.html', context)

#accepts a recommendation
@login_required
def accept_recc(request, recc_id):
    recc = Recommendation.objects.filter(id=recc_id).first()
    recc.accepted = True
    recc.save()
    reccs = Recommendation.objects.filter(accepted=False)
    context = {'reccs' : reccs}
    return render(request, 'albums/recommendation-review.html', context)

@login_required
def accept_and_add_recc(request, recc_id):
    recc = Recommendation.objects.filter(id=recc_id).first()
    recc.accepted = True
    recc.save()
    artist = Artist.objects.filter(name__iexact=recc.artist_name).first()
    if not artist:
        artist = Artist.objects.create(name=recc.artist_name)
    if recc.amazon_referral_url:
        Album.objects.create(
            name = recc.album_name,
            artist = artist,
            amazon_url = recc.amazon_referral_url
        )
    else:
        Album.objects.create(
            name = recc.album_name,
            artist = artist
        )
    reccs = Recommendation.objects.filter(accepted=False)
    context = {'reccs' : reccs}
    return render(request, 'albums/recommendation-review.html', context)
########## FUNCTIONS THAT THEN REDIRECT ###########
@login_required
def delete_album(request, album, artist):
    album = Album.objects.filter(slug=album, artist__slug=artist).first()
    message = "{} by {} was deleted.".format(album.name, album.artist.name)
    album.delete()
    context = {'message': message}
    return render(request, 'albums/message.html', context)

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

def report(request):
    problem = request.POST.get('problem')
    description = request.POST.get('description')
    name = request.POST.get('name')
    url = request.POST.get('url')
    most_recent_issue = ReportIssue.objects.all().order_by('-issue_num').first()
    if most_recent_issue:
        new_issue_num = most_recent_issue.issue_num + 1
    else:
        new_issue_num = 1
    ReportIssue.objects.create(
        issue_num = new_issue_num,
        selected_issue = problem,
        description = description,
        reporter = name,
        page = url
    )
    return render(request, 'albums/base.html')

#functions for the album match game
def random_num(maximum):
    return int(random.uniform(0, maximum))

def generate_choices(total_count):
    choices = []
    answer_int = random_num(total_count)
    choices.append(answer_int)
    for i in range(3):
        choices.append(unique_random_num(choices, total_count))
    albums = []
    letters = ['A', 'B', 'C', 'D']
    for i in range(4):
        albums.append({'letter' : letters[i], 'album' : convert_to_album(choices[i])})
    return albums

def unique_random_num(choices, maximum):
    num = random_num(maximum)
    while num in choices:
        num = random_num(maximum)
    return num

def convert_to_album(choice):
    return Album.objects.exclude(album_art=None)[choice]


############ TEST PAGES ####################
@login_required
def htmltest(request):
    context = {}
    albums = Album.objects.exclude(date_finished=None)
    albums, search, order_post, direction = search_albums(request.POST, albums)
    
    context.update({'albums': albums})
    context.update({
        'search' : search,
        'order' : order_post,
        'direction' : direction,
        'home' : 'active'
    })
    return render(request, 'albums/test.html', context)
