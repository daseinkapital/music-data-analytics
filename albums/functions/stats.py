from albums.models import *

#aggregations
from django.db.models import Avg, Sum

from datetime import datetime, date

#generates all necessary data for creating the table of genre statistics
def generate_genre_table(albums):
    genre_table = []
    for genre in PrimaryGenre.objects.all():
        #count of genre
        count = albums.filter(primary_genre=genre).count()

        #average rating of genre
        album_genre = albums.filter(primary_genre=genre)
        avg_rating = average_rating(album_genre)

        #minimum of genre
        min_album = albums.filter(primary_genre=genre).exclude(current_rating=None).order_by('current_rating').first()
        if min_album:
            min_rating = round(min_album.current_rating, 1)
        else:
            min_rating = "N/A"

        #maximum of genre
        max_album = albums.filter(primary_genre=genre).exclude(current_rating=None).order_by('-current_rating').first()
        if max_album:
            max_rating = round(max_album.current_rating, 1)
        else:
            max_rating = "N/A"

        #standard deviation of genre ratings
        if (avg_rating != 0) and (count > 10):
            numerator = 0
            denominator = count - 1
            for album in albums.filter(primary_genre=genre).exclude(current_rating=None):
                numerator += (float(album.current_rating) - float(avg_rating))**2
            stddev = round((numerator/denominator)**(0.5), 4)
        else:
            stddev = "N/A"

        genre_table.append({
            'genre' : genre,
            'count': count,
            'avg_rating' : avg_rating,
            'min_rating' : min_rating,
            'max_rating' : max_rating,
            'stddev' : stddev
        })
    return genre_table

#finds the average amount of new music I've listened to per day since the start of this project
def average_listen_time_per_day(query):
    music_since_start = query.exclude(chart=0)
    music_since_start_listened = music_since_start.exclude(date_finished=None)
    total_time = time_total_no_format(music_since_start_listened)
    days_delta = date.today() - date(2017, 1, 1)
    days_since_start = days_delta.days
    music_per_day = total_time/days_since_start
    return format_sum_time(music_per_day)

def queue_completion_time(albums, queue):
    music_from_last_month = Album.objects.filter(date_finished__gte=(date.today() - dt.timedelta(days=31)))
    if len(music_from_last_month) == 0:
        return "A lot of"
    total_time = time_total_no_format(music_from_last_month)
    days_delta = date.today() - (date.today() - dt.timedelta(days=31))
    days_since_start = days_delta.days
    music_per_day = total_time/days_since_start
    total_time = time_total_no_format(queue)
    queue_time = total_time
    return int(round(queue_time.total_seconds()/music_per_day.total_seconds(),0))
    

#given a query of albums, returns the total length of time of all albums collectively
def time_total(query):
    total_time = time_total_no_format(query)
    return format_sum_time(total_time)


def time_total_no_format(query):
    total_time = dt.timedelta(seconds=0)
    for item in query:
        if item.time_length:
            total_time += item.time_length
    return total_time
#average rating of a query
def average_rating(query):
    #average rating of genre
    avg_rating = query.exclude(current_rating=None).aggregate(Avg('current_rating'))['current_rating__avg']
    if avg_rating != None:
        avg_rating = round(avg_rating, 4)
    else:
        avg_rating = 0
    return avg_rating


###### HELPER FUNCTIONS
#takes a time delta and nicely formats to a string
def format_sum_time(sum_time):
    hours, remainder = divmod(sum_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if sum_time.days:
        return '{:02}d {:02}h {:02}m {:02}s'.format(int(sum_time.days), int(hours), int(minutes), int(seconds))
    else:
        return '{:02}h {:02}m {:02}s'.format(int(hours), int(minutes), int(seconds))