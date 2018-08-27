from django.db import models

# Create your models here.
class Artist(models.Model):
    name = models.CharField(
        max_length=256,
    )

class PrimaryGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )

class SubGenre(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
    )
    
class Rating(models.Model):
    score = models.IntegerField(
        null=True,
        blank=True,
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
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    sub_genre = models.ManyToManyField(
        'SubGenre',
        blank=True,
        null=True,
    )

    time_length = models.DurationField(
        null=True,
        blank=True,
    )

    release_date = models.DateField(
        null=True,
        blank=True,
    )

    album_art = models.URLField(
        null=True,
        blank=True,
    )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def time_check(self):
        if self.time_length != "":
            return False
        else:
            return True

    def release_date_check(self):
        if self.release_date != "":
            return False
        else:
            return True

    def album_art_check(self):
        if self.album_art != "":
            return False
        else:
            return True

    def all_info_found(self):
        if not self.album_art_check() and not self.release_date_check() and not self.time_length_check():
            return True
        else:
            return False
    
    def in_queue(self):
        if self.date_finished:
            return False
        else:
            return True
