from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register(prefix='matchups', viewset=views.MatchupViewSet, basename='matchup')
router.register(prefix='poolhouses', viewset=views.PoolHouseViewSet, basename='poolhouse')
router.register(prefix='invitations', viewset=views.MatchMakeViewSet, basename='matchmake')
router.register(prefix='players', viewset=views.PlayerViewSet,basename='player')
router.register(prefix='history', viewset=views.HistoryViewSet, basename='history')

tables_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
tables_router.register(prefix='tables', viewset=views.TableViewSet, basename='table')

reservations_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
reservations_router.register(prefix='reservations', viewset=views.ReservationViewSet, basename='reservation')

ratings_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
ratings_router.register(prefix='ratings', viewset=views.PoolHouseRatingViewSet, basename='rating')

game_session_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
game_session_router.register(prefix='game-sessions', viewset=views.GameSessionControlViewSet, basename='game-session')

urlpatterns = router.urls + tables_router.urls + reservations_router.urls + ratings_router.urls + game_session_router.urls





