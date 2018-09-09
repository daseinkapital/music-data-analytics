from django.test import TestCase
from .models import *
from .management.commands import adddata

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

class ScrapeDataUnitTest(TestCase):
    def test_find_wiki_url_plain_case(self):
        artist = Artist.objects.create(
            name = "The Rolling Stones"
        )

        album = Album.objects.create(
            name = "Let It Bleed",
            artist = artist
        )

        url = adddata.find_wiki_urls(album)
        self.assertEqual(url, 'https://en.wikipedia.org/wiki/Let_It_Bleed')

    def test_find_wiki_url_album(self):
        artist = Artist.objects.create(
            name = "Glass Animals"
        )

        album = Album.objects.create(
            name = "Zaba",
            artist = artist
        )

        url = adddata.find_wiki_urls(album)
        self.assertEqual(url, 'https://en.wikipedia.org/wiki/Zaba_(album)')

    def test_find_wiki_url_album_and_artist(self):
        artist = Artist.objects.create(
            name = "The National"
        )

        album = Album.objects.create(
            name = "Alligator",
            artist = artist
        )

        url = adddata.find_wiki_urls(album)
        self.assertEqual(url, 'https://en.wikipedia.org/wiki/Alligator_(The_National_album)')

    def test_wiki_parse_date_day_month_year(self):
        date_str = '10 January 1996'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertEqual('%d %B %Y', return_str)
    
    def test_wiki_parse_date_month_day_year_comma(self):
        date_str = 'January 10, 1996'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertEqual('%B %d, %Y', return_str)

    def test_wiki_parse_date_month_day_year_no_comma(self):
        date_str = 'January 10 1996'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertEqual('%B %d %Y', return_str)

    def test_wiki_parse_date_month_year(self):
        date_str = 'January 1996'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertEqual('%B %Y', return_str)

    def test_wiki_parse_date_year(self):
        date_str = '1996'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertEqual('%Y', return_str)

    def test_wiki_parse_date_none(self):
        date_str = ''
        return_str = adddata.wiki_parse_date(date_str)
        self.assertFalse(return_str)

    def test_wiki_parse_date_unrecognized_pattern(self):
        date_str = '1996 10 January'
        return_str = adddata.wiki_parse_date(date_str)
        self.assertFalse(return_str)

class ScrapeDataEdgeCaseTests(TestCase):
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

        self.artist4 = Artist.objects.create(
            name = "runescape斯凱利"
        )

        self.artist5 = Artist.objects.create(
            name = "Streetlamps for Spotlights"
        )

        self.artist6 = Artist.objects.create(
            name = "2 8 1 4"
        )

        self.artist7 = Artist.objects.create(
            name = "Taylor Davis"
        )

        self.album1 = Album.objects.create(
            artist = self.artist1,
            name = "Let It Bleed"
        )

        self.album2 = Album.objects.create(
            artist = self.artist2,
            name = "The Black Album"
        )

        self.album3 = Album.objects.create(
            artist = self.artist3,
            name = "Odyssey"
        )

        self.album4 = Album.objects.create(
            artist = self.artist4,
            name = "runescape​.​wav符文風景骨架"
        )

        self.album5 = Album.objects.create(
            artist = self.artist5,
            name = "Sound and Color"
        )

        self.album6 = Album.objects.create(
            artist = self.artist6,
            name = "新しい日の誕生"
        )

        self.album7 = Album.objects.create(
            artist = self.artist7,
            name = "Odyssey"
        )

    def test_album_on_wikipedia_time(self):
        adddata.scrape(self.album1)
        time = dt.timedelta(minutes=42, seconds=21)
        self.assertEqual(self.album1.time_length, time)
        
    def test_album_on_wikipedia_release_date(self):
        adddata.scrape(self.album1)
        date = dt.datetime.strptime('5 December 1969', '%d %B %Y')
        self.assertEqual(self.album1.release_date, date)
    
    def test_album_on_wikipedia_album_art(self):
        adddata.scrape(self.album1)
        album_art = "//upload.wikimedia.org/wikipedia/en/thumb/c/c0/LetitbleedRS.jpg/220px-LetitbleedRS.jpg"
        self.assertEqual(self.album1.album_art, album_art)

    def test_album_on_wikipedia_by_different_artists_time(self):
        adddata.scrape(self.album2)
        time = dt.timedelta(minutes=55, seconds=32)
        self.assertEqual(self.album2.time_length, time)

    def test_album_on_wikipedia_by_different_artists_release_date(self):
        adddata.scrape(self.album2)
        release_date =  dt.datetime.strptime('November 14, 2003', '%B %d, %Y')
        self.assertEqual(self.album2.release_date, release_date)
    
    def test_album_on_wikipedia_by_different_artists_album_art(self):
        adddata.scrape(self.album2)
        album_art = "//upload.wikimedia.org/wikipedia/en/thumb/0/0e/Jay-Z_-_The_Black_Album.png/220px-Jay-Z_-_The_Black_Album.png"
        self.assertEqual(self.album2.album_art, album_art)

    def test_album_only_on_bandcamp_time(self):
        adddata.scrape(self.album3)
        time = dt.timedelta(minutes=47, seconds=41)
        self.assertEqual(self.album3.time_length, time)
        
    def test_album_only_on_bandcamp_release_date(self):
        adddata.scrape(self.album3)
        release_date = dt.datetime.strptime('July 1, 2014', '%B %d, %Y')
        self.assertEqual(self.album3.release_date, release_date)
        
    def test_album_only_on_bandcamp_album_art(self):
        adddata.scrape(self.album3)
        album_art = "https://f4.bcbits.com/img/a3321951232_16.jpg"
        self.assertEqual(self.album3.album_art, album_art)

    def test_album_that_uses_characters_from_different_language_time(self):
        adddata.scrape(self.album4)
        time = dt.timedelta(minutes=54, seconds=44)
        self.assertEqual(self.album4.time_length, time)

    def test_album_that_uses_characters_from_different_language_release_date(self):
        adddata.scrape(self.album4)
        release_date = dt.datetime.strptime('January 22, 2018', '%B %d, %Y')
        self.assertEqual(self.album4.release_date, release_date)

    def test_album_that_uses_characters_from_different_language_album_art(self):
        adddata.scrape(self.album4)
        album_art = "https://f4.bcbits.com/img/a2793267385_16.jpg"
        self.assertEqual(self.album4.album_art, album_art)

    def test_album_on_bandcamp_with_name_that_is_also_on_wiki_time(self):
        adddata.scrape(self.album5)
        time = dt.timedelta(minutes=33 , seconds=36)
        self.assertEqual(self.album5.time_length, time)

    def test_album_on_bandcamp_with_name_that_is_also_on_wiki_release_date(self):
        adddata.scrape(self.album5)
        release_date = dt.datetime.strptime('April 19, 2014', '%B %d, %Y')
        self.assertEqual(self.album5.release_date, release_date)

    def test_album_on_bandcamp_with_name_that_is_also_on_wiki_album_art(self):
        adddata.scrape(self.album5)
        album_art = "https://f4.bcbits.com/img/a3345060228_16.jpg"
        self.assertEqual(self.album5.album_art, album_art)

    def test_album_completely_in_another_language_time(self):
        adddata.scrape(self.album6)
        time = dt.timedelta(minutes=67 , seconds=23)
        self.assertEqual(self.album6.time_length, time)

    def test_album_completely_in_another_language_release_date(self):
        adddata.scrape(self.album6)
        release_date = dt.datetime.strptime('January 21, 2015', '%B %d, %Y')
        self.assertEqual(self.album6.release_date, release_date)

    def test_album_completely_in_another_language_album_art(self):
        adddata.scrape(self.album6)
        album_art = "https://f4.bcbits.com/img/a4099353330_16.jpg"
        self.assertEqual(self.album6.album_art, album_art)

    def test_album_on_bandcamp_second_page_time(self):
        adddata.scrape(self.album7)
        time = dt.timedelta(minutes=43 , seconds=44)
        self.assertEqual(self.album7.time_length, time)

    def test_album_on_bandcamp_second_page_release_date(self):
        adddata.scrape(self.album7)
        release_date = dt.datetime.strptime('October 28, 2016','%B %d, %Y')
        self.assertEqual(self.album7.release_date, release_date)

    def test_album_on_bandcamp_second_page_album_art(self):
        adddata.scrape(self.album7)
        album_art = "https://f4.bcbits.com/img/a2565743238_16.jpg"
        self.assertEqual(self.album7.album_art, album_art)

    # def test_album_on_wikipedia_self_titled_time(self):
    #     adddata.scrape(self.album8)
    #     time = dt.timedelta(minutes= , seconds= )
    #     self.assertEqual(self.album8.time_length, time)

    # def test_album_on_wikipedia_self_titled_released_date(self):
    #     adddata.scrape(self.album8)
    #     release_date = dt.datetime.strptime('', '%B %d, %Y')
    #     self.assertEqual(self.album8.time_length, time)

    # def test_album_on_wikipedia_self_titled_album_art(self):
    #     adddata.scrape(self.album8)
    #     time = dt.timedelta(minutes= , seconds= )
    #     self.assertEqual(self.album8.time_length, time)