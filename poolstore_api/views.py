from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from poolstore.models import GameSession, History, Invitation, InvitationDenied, Matchup, Message, Notification, Player, PoolHouse, PoolHouseImage, PoolHouseRating, PoolTable, Reservation
from poolstore_api.serializers import CreateHistorySerializer, GameSessionSerializer, InvitationSerializer, ListHistorySerializer, MatchupSerializer, MessageSerializer, NotificationSerializer, PlayerSerializer, PoolHouseImageSerializer, PoolHouseRatingSerializer, PoolHouseSerializer, PoolTableSerializer, ReservationSerializer, SimplePoolHouseSerializer, StaffReservationCreateSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin
from poolstore_api.serializers import CreateHistorySerializer, DetailPlayerSerializer, GameSessionSerializer, InvitationSerializer, ListHistorySerializer, MatchupSerializer, MessageSerializer, NotificationSerializer, PlayerSerializer, PoolHouseImageSerializer, PoolHouseRatingSerializer, PoolHouseSerializer, PoolTableSerializer, ReservationSerializer, SimplePoolHouseSerializer, StaffReservationCreateSerializer
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly, IsCurrentUserOrReadOnly, IsPlayerReservingUserOrReadOnly, IsRaterOrReadOnly, IsStaffOrDenied, IsStaffOrReadOnly
from django.db.models import Q, Max
from .pagination import MessagePageNumberPagination, NotificationPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Avg, Count
from .tasks import finish_game_session
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from .utils import get_nearby_poolhouses, get_nearby_players
from celery.result import AsyncResult
from django.db.models import OuterRef, Prefetch
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView





class PoolHouseViewSet(ModelViewSet):
    queryset = PoolHouse.objects.annotate(
        avg_rating=Avg('ratings__rate'),
        table_count=Count('tables', distinct=True)
    ).prefetch_related('pics').prefetch_related('tables')

    serializer_class = PoolHouseSerializer
    permission_classes = [IsAdminOrReadOnly]


    # @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FilterPoolHouseViewSet(ListModelMixin, GenericViewSet):
    queryset = PoolHouse.objects.annotate(
        avg_rating=Avg('ratings__rate'),
        table_count=Count('tables', distinct=True)
    ).prefetch_related('pics').prefetch_related('tables')
    serializer_class = PoolHouseSerializer


    # @method_decorator(cache_page(60 * 5))
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
        

        
class ReservationViewSet(ListModelMixin, RetrieveModelMixin,DestroyModelMixin, GenericViewSet):
    http_method_names = ['get', 'head', 'options', 'delete']
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsPlayerReservingUserOrReadOnly]
    
    def get_queryset(self):
        queryset = Reservation.objects.filter(Q(player_reserving=self.request.user.player) | Q(other_player=self.request.user.player), finished_reservation=False) \
        .select_related('player_reserving__user').select_related('other_player__user')
        return queryset


    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        result = AsyncResult(f'custom_task_id_{reservation.id}')
        result.revoke()
        return super().destroy(request, *args, **kwargs)
    





class MatchupViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = MatchupSerializer
    pagination_class = MessagePageNumberPagination
    permission_classes = [IsAuthenticated]


    ## RAW SQL CODE WOULD BE BETTER HERE SINCE ALL MESSAGES ARE FETCHED    


    # SELECT m.*,
    #        MAX(msg.id) AS last_message_id,  -- Get the latest message id
    #        MAX(msg.time_sent) AS last_message_time
    # FROM poolstore_matchup m
    # LEFT JOIN poolstore_message msg ON m.id = msg.matchup_id
    # WHERE m.player_accepting_id = 11 OR m.player_inviting_id = 11
    # GROUP BY m.id
    # ORDER BY last_message_time DESC

    def get_queryset(self):
        queryset = Matchup.objects.filter(
                Q(player_accepting=self.request.user.player) | Q(player_inviting=self.request.user.player)
            ).select_related(
                'player_accepting__user', 'player_inviting__user'
            ).prefetch_related(
                Prefetch('messages', queryset=Message.objects.select_related('sender__user').order_by('-time_sent')[:1], to_attr='ordered_messages')
            ).annotate(last_message_time=Max('messages__time_sent')).order_by('-last_message_time')
        return queryset
    
    # Order first by matchup '-timestamp',
    

    @action(detail=True, methods=['GET'])
    def chat(self, request, pk):
        if self.request.method == 'GET':
            messages = Message.objects.filter(matchup_id=pk).select_related('sender__user').order_by('-time_sent')
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
        return Invitation.objects.filter(player_invited=self.request.user.player).select_related('player_invited__user').select_related('player_inviting__user')
    

class PlayerViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'options', 'head', 'delete']
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsCurrentUserOrReadOnly]
    filterset_fields = ['user__username']


    def get_queryset(self):
        return Player.objects.select_related('user').all()
    


class PoolHouseRatingViewSet(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet, CreateModelMixin):
    serializer_class = PoolHouseRatingSerializer
    permission_classes = [IsRaterOrReadOnly]

    def get_queryset(self):
        return PoolHouseRating.objects.filter(poolhouse_id=self.kwargs['poolhouse_pk'])
    
    def get_serializer_context(self):
        context = {}
        if self.request.user.is_authenticated:
            context['player'] = self.request.user.player

        context['poolhouse_pk'] = self.kwargs['poolhouse_pk']
        return context
    

class HistoryViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = History.objects.filter(Q(winner_player=self.kwargs['player_pk']) | Q(loser_player=self.kwargs['player_pk'])) \
        .select_related('winner_player__user').select_related('loser_player__user').select_related('poolhouse')
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
    


class PoolHouseReservationViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsStaffOrDenied]


    def get_queryset(self):
        return Reservation.objects.filter(table__poolhouse_id=self.kwargs['poolhouse_pk'], finished_reservation=False)



    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaffReservationCreateSerializer
        return ReservationSerializer

    def get_serializer_context(self):
        return {'poolhouse_id': self.kwargs['poolhouse_pk']}



class PoolHouseImageViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = PoolHouseImageSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return PoolHouseImage.objects.filter(poolhouse_id=self.kwargs['poolhouse_pk']).select_related('poolhouse')
    


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'poolhouse_id': self.kwargs['poolhouse_pk']})
        serializer.is_valid(raise_exception=True)
        
        poolhouse = serializer.save()

        poolhouse_serializer = PoolHouseSerializer(poolhouse, context=self.get_serializer_context())
        return Response(poolhouse_serializer.data, status=status.HTTP_201_CREATED)
    

class NotificationViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination


    def get_queryset(self):
        return Notification.objects.filter(player=self.request.user.player).order_by('-timestamp')


    


class MatchMakingPlayerViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]




    def get_queryset(self):
        current_player = self.request.user.player
        denied_invitations_id = current_player.denied_invitations.values_list('player_invited', flat=True)
        point_range = 200
        min_points = current_player.total_points - point_range
        max_points = current_player.total_points + point_range
        
        filter = self.request.query_params.get('filter')
        filter_location = self.request.query_params.get('filter_location')


        nearby_players = Player.objects \
        .exclude(id__in=denied_invitations_id) \
        .exclude(
        Q(sent_matchup_invitings__player_accepting=current_player) |
        Q(accepted_matchups__player_inviting=current_player)
        ) \
        .select_related('user')

        # TODO ADD CACHING
        if filter == 'rating':

            nearby_players = nearby_players.filter(total_points__gte=min_points, total_points__lte=max_points)

        nearby_players = nearby_players.filter(inviting_to_play=True).order_by('-total_points')

        if filter_location: 
            nearby_players = get_nearby_players(current_player.lat, current_player.lng, nearby_players.filter(lat__isnull=False, lng__isnull=False))

        return nearby_players


class DetailPlayerInfoView(APIView):
    # serializer_class = DetailPlayerSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Player.objects.filter(id=request.user.player.id).select_related('user').prefetch_related('received_invitations__player_inviting__user').first()
        serializer = DetailPlayerSerializer(queryset)
        return Response(serializer.data)


class PlayerLocationView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PlayerSerializer

    def get_queryset(self):
        return Player.objects.filter(user=self.request.user)


class ReadAllNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(player__user=self.request.user, read=False)

    def put(self, request, *args, **kwargs):
        updated_count = self.get_queryset().update(read=True)
        return Response({'updated_count': updated_count})



class ReadMatchupView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        matchup = get_object_or_404(Matchup, id=self.kwargs['matchup_id'])
        matchup.read = True
        matchup.save()
        cache.delete(f'matchup_{self.request.user.username}')
        cache.delete(f'{matchup.id}_reading')
        return Response({f'{matchup.id}': 'READ'})


class UnreadMatchupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_matchups_count = Matchup.objects.filter(
                Q(player_accepting=self.request.user.player) | Q(player_inviting=self.request.user.player)
            ).filter(read=False).count()
        

        return Response({'unread': unread_matchups_count})
