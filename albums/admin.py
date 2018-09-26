from django.contrib import admin
from .models import Album, Artist, PrimaryGenre, SubGenre, AlbumSubgenre, Rating, Recommendation, ListenURL

# Register your models here.
class AlbumAdmin(admin.ModelAdmin):
    pass
admin.site.register(Album, AlbumAdmin)

class ArtistAdmin(admin.ModelAdmin):
    pass
admin.site.register(Artist, ArtistAdmin)

class PrimaryGenreAdmin(admin.ModelAdmin):
    pass
admin.site.register(PrimaryGenre, PrimaryGenreAdmin)

class SubGenreAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubGenre, SubGenreAdmin)

class AlbumSubgenreAdmin(admin.ModelAdmin):
    pass
admin.site.register(AlbumSubgenre, AlbumSubgenreAdmin)

class RatingAdmin(admin.ModelAdmin):
    pass
admin.site.register(Rating, RatingAdmin)

class ReccAdmin(admin.ModelAdmin):
    pass
admin.site.register(Recommendation, ReccAdmin)

class ListenURLAdmin(admin.ModelAdmin):
    pass
admin.site.register(ListenURL, ListenURLAdmin)