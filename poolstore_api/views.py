from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from poolstore.models import PoolHouse, PoolTable
from poolstore_api.serializers import PoolHouseSerializer, PoolTableSerializer
from rest_framework.mixins import CreateModelMixin, ListModelMixin
# Create your views here.



class PoolHouseViewSet(ModelViewSet):
    queryset = PoolHouse.objects.all()
    serializer_class = PoolHouseSerializer


class TableViewSet(ModelViewSet):
    serializer_class = PoolTableSerializer
    def get_queryset(self):
        return PoolTable.objects.filter(poolhouse_id=self.kwargs['poolhouse_pk'])
    

