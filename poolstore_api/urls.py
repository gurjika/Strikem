from rest_framework_nested import routers
from . import views
from django.urls import path


router = routers.DefaultRouter()

router.register(prefix='matchups', viewset=views.MatchupViewSet, basename='matchup')
router.register(prefix='poolhouses', viewset=views.PoolHouseViewSet, basename='poolhouse')
router.register(prefix='invitations', viewset=views.MatchMakeViewSet, basename='matchmake')
router.register(prefix='players', viewset=views.PlayerViewSet,basename='player')
router.register(prefix='poolhouses-filter', viewset=views.FilterPoolHouseViewSet, basename='poolhouse-filter')
router.register(prefix='reservations', viewset=views.ReservationViewSet, basename='reservation')
router.register(prefix='notifications', viewset=views.NotificationViewSet, basename='notification')
router.register(prefix='filter-ratings', viewset=views.MatchMakingPlayerViewSet, basename='filter-rating')
# router.register(prefix='player-details', viewset=views.DetailPlayerInfoViewSet, basename='player-detail')

tables_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
tables_router.register(prefix='tables', viewset=views.TableViewSet, basename='table')

reservations_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
reservations_router.register(prefix='reservations', viewset=views.PoolHouseReservationViewSet, basename='reservation')

ratings_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
ratings_router.register(prefix='ratings', viewset=views.PoolHouseRatingViewSet, basename='rating')

game_session_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
game_session_router.register(prefix='game-sessions', viewset=views.GameSessionControlViewSet, basename='game-session')

poolhouse_image_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
poolhouse_image_router.register(prefix='images', viewset=views.PoolHouseImageViewSet, basename='image')

history_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='players', lookup='player')
history_router.register(prefix='history', viewset=views.HistoryViewSet, basename='history')



urlpatterns = router.urls + tables_router.urls + ratings_router.urls + game_session_router.urls + reservations_router.urls + poolhouse_image_router.urls + history_router.urls

urlpatterns += [ 
    path('player-details/', view=views.DetailPlayerInfoView.as_view(), name='player-detail'),
    path('player-location/', view=views.PlayerLocationView.as_view(), name='player-location'),
    path('mark-all-read/', view=views.ReadAllNotificationView.as_view(), name='mark-all-read'),
    path('read-matchup/<uuid:matchup_id>/', view=views.ReadMatchupView.as_view(), name='read-matchup')
]







