
import secrets
import string
from django.utils import timezone
from datetime import datetime, time, timedelta

import pytz
from core.models import User
from poolstore.models import Matchup, Message, Player, PoolHouse, Reservation
from django.db.models import Exists, OuterRef, Q, Subquery, Count

from django.core.cache import cache

def run():
    # PoolHouse.objects.create(title='MetroPool', address='Vera Park')


    # # date = '2024-6-19'
    # # date_v = datetime.strptime(date, '%Y-%m-%d').date()
    # # end_time = datetime(2024, 6, 19, 1, 0, 0)
    # # real_end_time = end_time + timedelta(minutes=5)
    # # start_time = time(0, 0, 0)
    # # date = date_v

    # # Reservation.objects.create(date=date_v, start_time=start_time, duration=30, end_time=end_time, real_end_time=real_end_time, table_id=1, player_id=1)

    # latest_message_subquery = Message.objects.filter(matchup=OuterRef('pk')) \
    # .order_by('-time_sent').values('sender')[:1]

    # unread_matchups = Matchup.objects.filter( \
    #     (Q(player_accepting=11) | Q(player_inviting=11))
    # ).filter(read=False).annotate(last_message_sender=Subquery(latest_message_subquery))

    # unread_matchups = unread_matchups.exclude(last_message_sender=11)
    
    # print(unread_matchups.query)

    # print(unread_matchups)
    days = 30
    time_threshold = timezone.now() - timezone.timedelta(days=days)
    players = Player.objects.annotate(
        cnt=Count('my_reservations', filter=Q(my_reservations__start_time__gte=time_threshold))
    ).filter(cnt__gt=0).order_by('-cnt').select_related('user')

    for player in players:
        print(player, player.cnt)