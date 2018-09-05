from django.db import models
from django.core.validators import URLValidator
from django.utils.text import slugify

# Create your models here.
class Artist(models.Model):
    name = models.CharField(
        max_length=256,
    )

    slug = models.SlugField()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super(Artist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class PrimaryGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )

    def __str__(self):
        return self.name

class SubGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )

    def __str__(self):
        return self.name
    
class Rating(models.Model):
    score = models.DecimalField(
        decimal_places=1,
        max_digits=4,
        null=True,
        blank=False,
    )

    listen = models.IntegerField(
        null=True,
        blank=True,
    )

    album = models.ForeignKey(
        to='Album',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return "{} received a {} on the {}{} listen.".format(self.album.name, str(self.score), str(self.listen), self.ending())

    def ending(self):
        if self.listen == 1:
            return "st"
        elif self.listen == 2:
            return "nd"
        elif self.listen == 3:
            return "rd"
        else:
            return "th"

class AlbumSubgenre(models.Model):
    album = models.ForeignKey(
        to='Album',
        related_name='subgenres',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    subgenre = models.ForeignKey(
        to='SubGenre',
        related_name='albums',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{} - {}".format(self.album.name, self.subgenre.name)

    class Meta:
        ordering = ['album', '-subgenre']

class Album(models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
    )

    artist = models.ForeignKey(
        to='Artist',
        related_name="albums",
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    order = models.IntegerField(
        null=True,
        blank=True,
    )

    chart = models.IntegerField(
        null=True,
        blank=True,
    )

    row = models.IntegerField(
        null=True,
        blank=True,
    )

    date_finished = models.DateField(
        blank=True,
        null=True,
    )

    primary_genre = models.ForeignKey(
        to='PrimaryGenre',
        related_name='albums',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    wiki_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    bc_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    time_length = models.DurationField(
        null=True,
        blank=True,
    )

    release_date = models.DateField(
        null=True,
        blank=True,
    )

    album_art = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        validators=[URLValidator()],
    )

    vinyl = models.BooleanField(
        default=False
    )

    cassette = models.BooleanField(
        default=False
    )

    slug = models.SlugField()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)[:50]
        super(Album, self).save(*args, **kwargs)

    @property
    def get_subgenres(self):
        album_subgenres = AlbumSubgenre.objects.filter(album = self)
        if album_subgenres:
            if len(album_subgenres) == 1:
                return album_subgenres.first().subgenre.name
            else:
                subgenre = album_subgenres.first().subgenre.name
                for genre in album_subgenres[1:]:
                    subgenre += ', {}'.format(genre.subgenre.name)
                return subgenre
        else:
            return None

    @property
    def average_rating(self):
        ratings = Rating.objects.filter(album=self)
        sum = 0
        count = ratings.count()
        for rating in ratings:
            sum += rating.score
        return sum/count

    def __str__(self):
        return "{} by {}".format(self.name, self.artist.name)
 
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def time_check(self):
        if self.time_length:
            return True
        else:
            return False

    def release_date_check(self):
        if self.release_date:
            return True
        else:
            return False

    def album_art_check(self):
        if self.album_art:
            return True
        else:
            return False

    def all_info_found(self):
        if self.album_art_check() and self.release_date_check() and self.time_check():
            return True
        else:
            return False
    
    def in_queue(self):
        if self.date_finished:
            return False
        else:
            return True

    def has_url(self):
        if self.wiki_url or self.bc_url:
            return True
        else:
            return False

    class Meta:
        ordering = ['name', 'artist']