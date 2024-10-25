from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from poolstore.models import GameSession, History, Invitation, Matchup, Message, Player, PoolHouse, PoolHouseRating, PoolTable, Reservation
from poolstore_api.serializers import CreateHistorySerializer, GameSessionSerializer, InvitationSerializer, ListHistorySerializer, MatchupSerializer, MessageSerializer, PlayerSerializer, PoolHouseRatingSerializer, PoolHouseSerializer, PoolTableSerializer, ReservationSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly, IsCurrentUserOrReadOnly, IsRaterOrReadOnly, IsStaffOrDenied
from django.db.models import Q
from .pagination import MessagePageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Avg
from .tasks import finish_game_session
from rest_framework import status
import os
import requests
from .utils import get_nearby_poolhouses


# Create your views here.



class PoolHouseViewSet(ModelViewSet):
    queryset = PoolHouse.objects.annotate(avg_rating=Avg('ratings__rate')).all()
    serializer_class = PoolHouseSerializer
    permission_classes = [IsAdminOrReadOnly]


    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FilterPoolHouseViewSet(ListModelMixin, GenericViewSet):
    queryset = PoolHouse.objects.annotate(avg_rating=Avg('ratings__rate')).all()
    serializer_class = PoolHouseSerializer


    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        user_lat = request.query_params.get('lat')
        user_lng = request.query_params.get('lng')
        venues = self.get_queryset()
        nearby_poolhouses = get_nearby_poolhouses(lat=user_lat, long=user_lng, poolhouses=venues)
   
        serializer = self.get_serializer(nearby_poolhouses, many=True)
        return Response(serializer.data)

class TableViewSet(ModelViewSet):
    serializer_class = PoolTableSerializer
    permission_classes = [IsAdminOrReadOnly]

    
    def get_queryset(self):
        return PoolTable.objects.filter(poolhouse_id=self.kwargs['poolhouse_pk'])



    def get_permissions(self):
        if self.action == 'reserve':
            if self.request.method == 'POST' or self.request.method == 'GET':
                permission_classes = [IsAuthenticated]  # Only authenticated users can reserve

        else:
            
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['POST', 'GET'])
    def reserve(self, request, pk, poolhouse_pk):

        if request.method == 'GET':
            
            filter_date = request.query_params.get('date')
            if filter_date:
                date_object = datetime.strptime(filter_date, "%Y-%m-%d")
                reservations = Reservation.objects.filter(table_id=pk,  start_time__range=[date_object, date_object + timedelta(days=1, hours=3)])
                serializer = ReservationSerializer(reservations, many=True)
                return Response(serializer.data)
            return Response({})

        if request.method == 'POST':
            serializer = ReservationSerializer(data=request.data, context={'table_id': pk, 'player': self.request.user.player})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        

        
class ReservationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, DestroyModelMixin):
    http_method_names = ['get', 'head', 'options', 'delete']
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Reservation.objects.filter(Q(player_reserving=self.request.user.player) | Q(other_player=self.request.user.player), finished_reservation=False)
        return queryset



class MatchupViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = MatchupSerializer
    pagination_class = MessagePageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Matchup.objects.filter(Q(player_accepting=self.request.user.player) | Q(player_inviting=self.request.user.player))
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @action(detail=True, methods=['GET'])
    def chat(self, request, pk):
        if self.request.method == 'GET':
            messages = Message.objects.filter(matchup_id=pk)
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = MessageSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)


class MatchMakeViewSet(ListModelMixin, GenericViewSet, RetrieveModelMixin):
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invitation.objects.filter(player_invited=self.request.user.player)
    

class PlayerViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'options', 'head', 'delete']
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsCurrentUserOrReadOnly]
    filterset_fields = ['user__username']


    def get_queryset(self):
        return Player.objects.all()
    


class PoolHouseRatingViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet, CreateModelMixin):
    serializer_class = PoolHouseRatingSerializer
    permission_classes = [IsRaterOrReadOnly]

    def get_queryset(self):
        return PoolHouseRating.objects.filter(poolhouse_id=self.kwargs['poolhouse_pk'])
    
    def get_serializer_context(self):
        return {'player': self.request.user.player, 'poolhouse_pk': self.kwargs['poolhouse_pk']}
    

class HistoryViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = History.objects.filter(Q(winner_player=self.request.user.player) | Q(loser_player=self.request.user.player))
        return queryset
    

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListHistorySerializer
        return CreateHistorySerializer
    

    def get_serializer_context(self):
        return {'player_id': self.request.user.player.id}
    

class GameSessionControlViewSet(ListModelMixin, DestroyModelMixin, GenericViewSet, RetrieveModelMixin):
    serializer_class = GameSessionSerializer
    authentication_classes = [IsStaffOrDenied]

    def get_queryset(self):
        return GameSession.objects.filter(poolhouse=self.kwargs['poolhouse_pk'])
    
    def destroy(self, request, *args, **kwargs):
        game_session = self.get_object()
        game_session.delete()
        return Response({"detail": "game session ended successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class PoolHouseReservationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsStaffOrDenied]


    def get_queryset(self):
        return Reservation.objects.filter(table__poolhouse_id=self.kwargs['poolhouse_pk'])


