from django.urls import path


from . import views
from . import spotifyviews

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
    path('admin-panel', views.admin_panel, name='admin-panel'),
    path('admin-panel/update/queue', views.update_album_queue, name="update-album-queue"),
    path('admin-panel/add/album/', views.add_album, name='add-album'),
    path('admin-panel/add/to-group/', views.add_album_to_group, name='add-album-to-group'),
    path('admin-panel/edit/<artist>/<album>/', views.edit_album, name='edit-album'),
    path('admin-panel/issue-manager/', views.issue_manager, name='issue-manager'),
    path('admin-panel/recc-review/', views.recommendations, name='recc-review'),
    path('admin-panel/accept-recc/<recc_id>/', views.accept_recc, name='accept_recc'),
    path('admin-panel/accept_and_add_recc/<recc_id>/', views.accept_and_add_recc, name='accept_and_add_recc'),
    path('admin-panel/delete-album/<album>/<artist>/', views.delete_album, name='delete-album'),
    path('admin-panel/update_album_artist/', views.update_information, name='update_album_info'),
    path('list/', views.lists, name='group-main'),
    path('spotify-login/', spotifyviews.spotifyLoginPage, name='spot-login'),
    path('features/', spotifyviews.experimental_features, name='experimental-features'),
    path('features/active-listening', spotifyviews.active_listening, name='active-listening'),
    path('list/<group>/', views.group, name='group'),
    path('chart/', views.chart_landing, name='chart-main'),
    path('chart/<chart_num>/', views.chart, name='chart'),
    path('suggest/', views.suggest, name='suggestion'),
    path('match-game/', views.match_game, name='game'),
    path('report/', views.report, name='report'),
    path('load-more-albums/', views.load_more_albums, name='load_more_albums'),
    path('test', views.htmltest, name='htmltest'),
]