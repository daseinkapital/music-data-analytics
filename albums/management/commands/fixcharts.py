from django.core.management.base import BaseCommand, CommandError
from albums.models import Album
from math import ceil

class Command(BaseCommand):
    help = 'Corrects error caused by creating chart numbers or mistakes among charts.'

    def handle(self, *args, **options):
        all_albums = Album.objects.exclude(order=0)
        sorted_albums = all_albums.order_by('order')
        redo_order_of_albums(sorted_albums)
        correct_the_chart(sorted_albums)
        correct_the_row(sorted_albums)


def redo_order_of_albums(albums):
    last_order = 0
    for album in albums:
        last_order += 1
        if album.order != last_order:
            album.order = last_order
            album.save()
        last_order = album.order

def correct_the_chart(albums):
    for album in albums:
        if album.order <= 144:
            if album.chart != 1:
                album.chart = 1
                album.save()
        elif album.order <= 288:
            if album.chart != 2:
                album.chart = 2
                album.save()
        elif album.order <= 432:
            if album.chart != 3:
                album.chart = 3
                album.save()
        elif album.order <= 576:
            if album.chart != 4:
                album.chart = 4
                album.save()
        else:
            chart_number = 4 + ceil((album.order - 576)/100)
            if album.chart != chart_number:
                album.chart = chart_number
                album.save()

def correct_the_row(albums):
    for album in albums:
        if album.order <= 576:
            order_on_chart = album.order - (144 * (album.chart - 1))
            row = ceil(order_on_chart/12)
            album.row = row
            album.save()
        else:
            order_on_chart = album.order - 576
            while order_on_chart > 100:
                order_on_chart -= 100
            row = ceil(order_on_chart/10)
            album.row = row
            album.save()