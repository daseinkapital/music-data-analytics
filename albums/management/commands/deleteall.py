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
        print(AlbumSubgenre.objects.all().count())
        print(Rating.objects.all().count())
        print(Album.objects.all().count())
        print(SubGenre.objects.all().count())
        print(PrimaryGenre.objects.all().count())
        print(Artist.objects.all().count())