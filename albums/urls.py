from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name="albums"),
    path('stats/', views.statistics, name="statistics"),
    path('artist/<artist>/<album>/', views.album_page, name="album-page"),
    path('artist/<artist>/', views.artist_page, name="artist-page"),
    path('genre/primary/<genre>/', views.primary_genre, name="primary-genre"),
    path('genre/secondary/<genre>/', views.secondary_genre, name="secondary-genre"),
    path('about', views.about, name="about"),
    path('htmltest', views.htmltest, name='htmltest'),
    path('list/<group>/', views.group, name='group'),
    path('chart/', views.chart_landing, name='chart-main'),
    path('chart/<chart_num>/', views.chart, name='chart'),
]