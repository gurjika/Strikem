from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register(prefix='matchups', viewset=views.MatchupViewSet, basename='matchup')
router.register(prefix='poolhouses', viewset=views.PoolHouseViewSet, basename='poolhouse')

tables_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
tables_router.register(prefix='tables', viewset=views.TableViewSet, basename='table')

reservations_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
reservations_router.register(prefix='reservations', viewset=views.ReservationViewSet, basename='reservation')

urlpatterns = router.urls + tables_router.urls + reservations_router.urls





