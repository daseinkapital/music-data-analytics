from django.db import models
from django.core.validators import URLValidator
from django.utils.text import slugify

import datetime as dt

from .management.commands.scrape import scrape_wiki, scrape_bc, scrape_amazon, screw_the_rules

# Create your models here.
class Artist(models.Model):
    name = models.CharField(
        max_length=256,
    )

    slug = models.SlugField()

    note = models.TextField(
        null=True,
        blank=True
    )

    seen_live = models.BooleanField(
        default = False
    )
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)[:50]
        super(Artist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class PrimaryGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )

    spotify_playlist = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class SubGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )

    spotify_playlist = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    note = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Rating(models.Model):
    score = models.DecimalField(
        decimal_places=1,
        max_digits=3,
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
        related_name="ratings"
    )

    class Meta:
        ordering = ['-listen']

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

class Song(models.Model):
    album = models.ForeignKey(
        to='Album',
        related_name='songs',
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    name = models.CharField(
        max_length=500,
        blank=False,
        null=False
    )

    favorite = models.BooleanField(
        default=False
    )

    least_favorite = models.BooleanField(
        default=False
    )

    track_num = models.IntegerField(
        null=True,
        blank=True
    )

    track_length = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

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

    amazon_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    discogs_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    itunes_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    spotify_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    soundcloud_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()],
    )

    youtube_url = models.TextField(
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
    
    current_rating = models.DecimalField(
        decimal_places=4,
        max_digits=6,
        null=True,
        blank=True,
    )

    note = models.TextField(
        null=True,
        blank=True
    )

    personally_checked = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)[:50]
        self.current_rating = self.average_rating

        if self.order == None:

            latest_album = Album.objects.exclude(order=None).order_by('-order').first()
            chart = latest_album.chart
            album_row_count = Album.objects.filter(chart=latest_album.chart, row=latest_album.row).count
            if album_row_count == 10:
                if latest_album.row == 10:
                    row = 1
                    chart = chart + 1
                else:
                    row = latest_album.row + 1
                    chart = latest_album.chart
            else:
                row = latest_album.row
                chart = latest_album.chart
            self.order = latest_album.order + 1
            self.row = row
            self.chart = chart

        if self.all_info_found():
            super(Album, self).save(*args, **kwargs)
        else:
            screw_the_rules()
            if self.amazon_url:
                self = scrape_amazon(self)
            if self.bc_url:
                self = scrape_bc(self)
            if self.wiki_url:
                self = scrape_wiki(self)
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
        if count != 0:
            for rating in ratings:
                sum += rating.score
            return sum/count
        else:
            return None

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
        if self.wiki_url or self.bc_url or self.amazon_url:
            return True
        else:
            return False
    
    def has_spotify(self):
        if self.playback_urls.all().first().spotify:
            return True
        else:
            return False

    def has_itunes(self):
        if self.playback_urls.all().first().itunes:
            return True
        else:
            return False

    def time_hours(self):
        return self.time_length.seconds//3600

    def time_minutes(self):
        return (self.time_length.seconds//60)%60
    
    def time_seconds(self):
        return self.time_length.seconds%60
    
    def display_listen_date(self):
        if self.date_finished:
            return self.date_finished > dt.datetime.strptime('01/02/2017', '%m/%d/%Y').date()
        else:
            return False

    class Meta:
        ordering = ['name', 'artist']

class Group(models.Model):
    name = models.CharField(
        max_length=250,
        null=False,
        blank=False
    )

    note = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name']

class AlbumGroup(models.Model):
    album = models.ForeignKey(
        to='Album',
        related_name='lists',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        to='Group',
        related_name='lists',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

class WikiSubgenre(models.Model):
    name = models.CharField(
        max_length=250,
        null=False,
        blank=False
    )

    url = models.URLField()

class BandcampSubgenre(models.Model):
    name = models.CharField(
        max_length=250,
        null=False,
        blank=False
    )

class Recommendation(models.Model):
    recommender = models.CharField(
        max_length = 100,
        null=False,
        blank=False
    )

    album_name = models.CharField(
        max_length = 256,
        null=False,
        blank=False
    )

    artist_name = models.CharField(
        max_length = 250,
        null=False,
        blank=False
    )

    genre = models.CharField(
        max_length = 250,
        null = True,
        blank=True
    )

    url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()]
    )

    amazon_referral_url = models.TextField(
        null=True,
        blank=True,
        validators=[URLValidator()]
    )

    note = models.TextField(
        null=True,
        blank=True
    )

    accepted = models.BooleanField(
        default=False
    )

    def __str__(self):
        return "{0} recommends {1} by {2}".format(self.recommender, self.album_name, self.artist_name)

class AlbumArtist(models.Model):
    artist = models.ForeignKey(
        to='Artist',
        related_name="all_albums",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    album = models.ForeignKey(
        to='Album',
        related_name="all_artists",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )