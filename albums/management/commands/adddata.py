from django.core.management.base import BaseCommand, CommandError

from albums.models import Album
from .scrape import scrape



class Command(BaseCommand):
    help = 'Adds additional data that needs to be webscraped.'

    def handle(self, *args, **options):
        albums = Album.objects.exclude(name__icontains="?")
        albums = albums.exclude(artist__name__icontains="?")
        albums = albums.exclude(name="")
        for album in albums:
            print(album)
            urls = scrape(album)