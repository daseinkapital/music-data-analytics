from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name="homepage"),
    path('stats/', views.statistics, name="statistics"),
    path('artist/<artist>/<album>/', views.album_page, name="album-page"),
    path('artist/<artist>/', views.artist_page, name="artist-page"),
    path('about', views.about, name="about"),
    path('search', views.search, name="search"),
    path('htmltest', views.htmltest, name='htmltest'),
]