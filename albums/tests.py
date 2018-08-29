from django.test import TestCase
from .models import *

import datetime as dt

# Create your tests here.
class ModelsTests(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(
            name="The Beatles"
        )
        
        self.primary_genre = PrimaryGenre.objects.create(
            name="Rock"
        )
        
        self.subgenre1 = SubGenre.objects.create(
            name="Pysch Rock"
        )
        
        self.subgenre2 = SubGenre.objects.create(
            name="Classic Rock"
        )
        
        self.album1 = Album.objects.create(
            name = "Yellow Submarine",
            artist = self.artist,
            primary_genre = self.primary_genre,
            order = 1,
            chart = 1,
            row = 1,
            time_length = dt.timedelta(minutes=54, seconds=12),
            release_date = dt.datetime.strptime('January 15, 1968', '%B %d, %Y'),
            album_art = "https://i0.wp.com/thenewtropic.com/wp-content/uploads/sites/2/2018/07/o-cinema-yellow-submarine.jpg?fit=744%2C808&ssl=1"
        )

        self.album2 = Album.objects.create(
            name = "Rubber Soul",
            artist = self.artist,
            primary_genre = self.primary_genre,
            order = 2,
            chart = 1,
            row = 1
        )

        AlbumSubgenre.objects.create(
            album = self.album1,
            subgenre = self.subgenre1
        )

        AlbumSubgenre.objects.create(
            album = self.album1,
            subgenre = self.subgenre2
        )

        AlbumSubgenre.objects.create(
            album = self.album2,
            subgenre = self.subgenre2
        )

        self.rating1 = Rating.objects.create(
            score = 5,
            listen = 1,
            album = self.album1
        )

        self.rating2 = Rating.objects.create(
            score = 7,
            listen = 2,
            album = self.album1
        )

        self.rating3 = Rating.objects.create(
            score = 8.5,
            listen = 3,
            album = self.album1
        )

        self.rating4 = Rating.objects.create(
            score = 7,
            listen = 4,
            album = self.album1
        )

    def test_artist_name(self):
        self.assertEqual(self.artist.name, "The Beatles")

    def test_primary_genre_name(self):
        self.assertEqual(self.primary_genre.name, "Rock")
    
    def test_subgenre_name(self):
        self.assertEqual(self.subgenre1.name, "Pysch Rock")
    
    def test_ratings_ending_1st(self):
        self.assertEqual(self.rating1.ending(), "st")
    
    def test_ratings_ending_2nd(self):
        self.assertEqual(self.rating2.ending(), "nd")
    
    def test_ratings_ending_3rd(self):
        self.assertEqual(self.rating3.ending(), "rd")

    def test_ratings_ending_4th(self):
        self.assertEqual(self.rating4.ending(), "th")

    def test_album_no_subgenre(self):
        album3 = self.album1
        album3.name = "The White Album"
        self.assertTrue(album3.get_subgenres, None)

    def test_album_single_subgenre(self):
        self.assertEqual(self.album2.get_subgenres, "Classic Rock")
    
    def test_album_multiple_subgenres(self):
        self.assertEqual(self.album1.get_subgenres, "Classic Rock, Pysch Rock")
    
    def test_album_average_rating(self):
        self.assertEqual(self.album1.average_rating, 6.875)

    def test_album_time_check_true(self):
        self.assertTrue(self.album1.time_check())
    
    def test_album_time_check_false(self):
        self.assertFalse(self.album2.time_check())

    def test_album_release_date_check_true(self):
        self.assertTrue(self.album1.release_date_check())

    def test_album_release_date_check_false(self):
        self.assertFalse(self.album2.release_date_check())

    def test_album_album_art_check_true(self):
        self.assertTrue(self.album1.album_art_check())

    def test_album_album_art_check_false(self):
        self.assertFalse(self.album2.album_art_check())

    def test_album_all_info_found_true(self):
        self.assertTrue(self.album1.all_info_found())

    def test_album_all_info_found_false(self):
        self.assertFalse(self.album2.all_info_found())
    
    def test_album_all_info_found_partial_info(self):
        self.album2.album_art = "https://upload.wikimedia.org/wikipedia/en/thumb/7/74/Rubber_Soul.jpg/220px-Rubber_Soul.jpg"
        self.assertFalse(self.album2.all_info_found())

# class ManagementCommandTests(TestCase):
