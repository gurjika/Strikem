from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()


router.register(prefix='poolhouses', viewset=views.PoolHouseViewSet, basename='poolhouse')


urlpatterns = router.urls