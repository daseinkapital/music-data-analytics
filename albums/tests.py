from django.test import TestCase
from .models import *
from .management/commands import adddata

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

class ManagementCommandTests(TestCase):
    def setUp(self):
        self.artist1 = Artist.objects.create(
            name = "The Rolling Stones"
        )

        self.artist2 = Artist.objects.create(
            name = "Jay-Z"
        )

        self.artist3 = Artist.objects.create(
            name = "Home"
        )

    def test_adddata_album_on_wikipedia_time(self):
        alb = Album.object.create("The Rolling Stones", "Let It Bleed")
        scrape(alb)
        time = dt.timedelta(minutes=42, seconds=21)
        self.assertEqual(alb.time, time)
        
    def test_adddata_album_on_wikipedia_release_date(self):
        alb = make_album("The Rolling Stones", "Let It Bleed")
        scrape(alb)
        date = dt.datetime.strptime('5 December 1969', '%d %B %Y')
        self.assertEqual(alb.release_date, date)
    
    def test_adddata_album_on_wikipedia_album_art(self):
        alb = make_album("The Rolling Stones", "Let It Bleed")
        scrape(alb)
        album_art = "//upload.wikimedia.org/wikipedia/en/thumb/c/c0/LetitbleedRS.jpg/220px-LetitbleedRS.jpg"
        self.assertEqual(alb.album_art, album_art)

    def test_adddata_album_on_wikipedia_by_different_artists(self):
        alb1 = make_album("Jay-Z", "The Black Album")
        scrape(alb1)
        alb2 = make_album("Jay-Z", "The Black Album")
        alb2.time = dt.timedelta(minutes=55, seconds=32)
        alb2.release_date =  dt.datetime.strptime('November 14, 2003', '%B %d, %Y')
        alb2.album_art = "//upload.wikimedia.org/wikipedia/en/thumb/0/0e/Jay-Z_-_The_Black_Album.png/220px-Jay-Z_-_The_Black_Album.png"
        self.assertEqual(alb1, alb2)

    def test_adddata_album_only_on_bandcamp_time(self):
        alb = make_album("Home", "Odyssey")
        scrape(alb)
        time = dt.timedelta(minutes=47, seconds=41)
        self.assertEqual(alb.time, time)
        
    def test_adddata_album_only_on_bandcamp_release_date(self):
        alb = make_album("Home", "Odyssey")
        scrape(alb)
        date = dt.datetime.strptime('July 1, 2014', '%B %d, %Y')
        self.assertEqual(alb.release_date, date)
        
    def test_adddata_album_only_on_bandcamp_album_art(self):
        alb = make_album("Home", "Odyssey")
        scrape(alb)
        album_art = "https://f4.bcbits.com/img/a3321951232_16.jpg"
        self.assertEqual(alb.album_art, album_art)

    def test_adddata_album_that_uses_characters_from_different_language(self):
        alb1 = make_album("runescape斯凱利", "runescape​.​wav符文風景骨架")
        scrape(alb1)
        alb2 = make_album("runescape斯凱利", "runescape​.​wav符文風景骨架")
        alb2.time = dt.timedelta(minutes=54, seconds=44)
        alb2.release_date = dt.datetime.strptime('January 22, 2018', '%B %d, %Y')
        alb2.album_art = "https://f4.bcbits.com/img/a2793267385_16.jpg"
        self.assertEqual(alb1, alb2)

    def test_adddata_album_on_bandcamp_with_name_that_is_also_on_wiki(self):
        alb1 = make_album("Streetlamps for Spotlights", "Sound and Color")
        scrape(alb1)
        alb2 = make_album("Streetlamps for Spotlights", "Sound and Color")
        alb2.time = dt.timedelta(minutes=33 , seconds=36)
        alb2.release_date = dt.datetime.strptime('April 19, 2014', '%B %d, %Y')
        alb2.album_art = "https://f4.bcbits.com/img/a3345060228_16.jpg"
        self.assertEqual(alb1, alb2)

    def test_adddata_album_completely_in_another_language(self):
        alb1 = make_album("2 8 1 4","新しい日の誕生")
        scrape(alb1)
        alb2 = make_album("2 8 1 4","新しい日の誕生")
        alb2.time = dt.timedelta(minutes=67 , seconds=23)
        alb2.release_date = dt.datetime.strptime('January 21, 2015', '%B %d, %Y')
        alb2.album_art = "https://f4.bcbits.com/img/a4099353330_16.jpg"
        self.assertEqual(alb1, alb2)

    def test_adddata_album_on_bandcamp_second_page(self):
        alb1 = make_album("Taylor Davis", "Odyssey")
        scrape(alb1)
        alb2 = make_album("Taylor Davis", "Odyssey")
        alb2.time = dt.timedelta(minutes=43 , seconds=44)
        alb2.release_date = dt.datetime.strptime('October 28, 2016','%B %d, %Y')
        alb2.album_art = "https://f4.bcbits.com/img/a2565743238_16.jpg"
        self.assertEqual(alb1, alb2)
