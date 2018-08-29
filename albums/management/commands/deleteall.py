from django.core.management.base import BaseCommand, CommandError
from albums.models import Artist, PrimaryGenre, SubGenre, Rating, Album, AlbumSubgenre

class Command(BaseCommand):
    help = 'Clears out all objects in the database.'

    def handle(self, *args, **options):
        AlbumSubgenre.objects.all().delete()
        Rating.objects.all().delete()
        Album.objects.all().delete()
        SubGenre.objects.all().delete()
        PrimaryGenre.objects.all().delete()
        Artist.objects.all().delete()