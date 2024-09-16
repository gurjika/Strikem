from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()


router.register(prefix='poolhouses', viewset=views.PoolHouseViewSet, basename='poolhouse')

tables_router = routers.NestedDefaultRouter(parent_router=router, parent_prefix='poolhouses', lookup='poolhouse')
tables_router.register(prefix='tables', viewset=views.TableViewSet, basename='table')

urlpatterns = router.urls + tables_router.urls