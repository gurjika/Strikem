from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from poolstore.models import PoolHouse
from poolstore_api.serializers import PoolHouseSerializer
# Create your views here.



class PoolHouseViewSet(ModelViewSet):
    queryset = PoolHouse.objects.all()
    serializer_class = PoolHouseSerializer


