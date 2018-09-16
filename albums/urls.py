from django.urls import path


from . import views

urlpatterns = [
    path('', views.main, name="home"),
    path('stats/', views.statistics, name="statistics"),
    path('artist/<artist>/<album>/', views.album_page, name="album-page"),
    path('artist/<artist>/', views.artist_page, name="artist-page"),
    path('genre/primary/<genre>/', views.primary_genre, name="primary-genre"),
    path('genre/secondary/<genre>/', views.secondary_genre, name="secondary-genre"),
    path('about', views.about, name="about"),
    path('test', views.htmltest, name='htmltest'),
    path('list/<group>/', views.group, name='group'),
    path('chart/', views.chart_landing, name='chart-main'),
    path('chart/<chart_num>/', views.chart, name='chart'),
    path('edit/<artist>/<album>/', views.edit_album, name='edit-album'),
    path('add/album/', views.add_album, name='add-album'),
    path('suggest/', views.suggest, name='suggestion'),
    path('page-not-found', views.page_not_found, name='404'),
    path('this-is-on-us', views.internal_server_error, name='500')
]