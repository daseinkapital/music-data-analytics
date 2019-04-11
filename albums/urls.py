from django.urls import path


from . import views

urlpatterns = [
    path('', views.main, name='home'),
    path('stats/', views.statistics, name='statistics'),
    path('artist/<artist>/<album>/', views.album_page, name='album-page'),
    path('artist/<artist>/', views.artist_page, name='artist-page'),
    path('genre/primary/<genre>/', views.primary_genre, name='primary-genre'),
    path('genre/primary/', views.prime_genre_landing, name='primary-genre-landing'),
    path('genre/secondary/<genre>/', views.secondary_genre, name='secondary-genre'),
    path('genre/secondary/', views.subgenre_landing, name='subgenre-landing'),
    path('consolidate-subgenre/', views.consolidate_subgenre, name='change-subgenres'),
    path('about', views.about, name='about'),
    path('list/', views.lists, name='group-main'),
    path('list/<group>/', views.group, name='group'),
    path('chart/', views.chart_landing, name='chart-main'),
    path('chart/<chart_num>/', views.chart, name='chart'),
    path('edit/<artist>/<album>/', views.edit_album, name='edit-album'),
    path('add/album/', views.add_album, name='add-album'),
    path('add/to-group/', views.add_album_to_group, name='add-album-to-group'),
    path('suggest/', views.suggest, name='suggestion'),
    path('match-game/', views.match_game, name='game'),
    path('issue-manager/', views.issue_manager, name='issue-manager'),
    path('recc-review/', views.recommendations, name='recc-review'),
    path('accept-recc/<recc_id>/', views.accept_recc, name='accept_recc'),
    path('accept_and_add_recc/<recc_id>/', views.accept_and_add_recc, name='accept_and_add_recc'),
    path('delete-album/<album>/<artist>/', views.delete_album, name='delete-album'),
    path('report/', views.report, name='report'),
    path('load-more-albums/', views.load_more_albums, name='load_more_albums'),
    path('update_album_artist/', views.update_information, name='update_album_info'),
    path('test', views.htmltest, name='htmltest'),
]