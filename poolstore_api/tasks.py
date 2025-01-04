from datetime import timedelta
from celery import shared_task
from channels.layers import get_channel_layer
from poolstore.models import GameSession, PlayerGameSession, PoolTable, Reservation
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.timezone import now


User = get_user_model()


@shared_task
def start_game_session(reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    game_session = GameSession.objects.create(pooltable=reservation.table)

    if reservation.other_player:
        PlayerGameSession.objects.create(game_session=game_session, player=reservation.other_player)
    
    PlayerGameSession.objects.create(game_session=game_session, player=reservation.player_reserving)
    
    finish_game_session.apply_async((
        game_session.id, reservation.id, 'Finished'), 
        eta=reservation.end_time, 
        task_id=f'game_session_{game_session.id}'
    )
    

    event = {
        'type': 'update_table',
        'table_id': reservation.table.table_id,
        'protocol': 'now_busy'
    }

    channel_layer = get_channel_layer()
    game_session.pooltable.free = False
    game_session.save()

    async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)




@shared_task
def finish_game_session(game_session_id, reservation_id, protocol):
    game_session = GameSession.objects.get(id=game_session_id)
    reservation = Reservation.objects.get(id=reservation_id)
    channel_layer = get_channel_layer()
    
    if protocol == 'Finished':
        event = {
            'type': 'finish_game_session',
        }
    else:
        event = {
            'type': 'abort_game_session'
        }

    for player in game_session.players.all():
        async_to_sync(channel_layer.group_send)(f'user_{player.user.username}', event)

    event = {
        'type': 'update_table',
        'table_id': reservation.table.table_id,
        'protocol': 'now_free'
    }


    async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)

    game_session.pooltable.free = True
    game_session.status_finished = True
    reservation.finished_reservation = True
    reservation.save()
    game_session.save()




    

@shared_task
def send_email_before_res():
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=now() + timedelta(minutes=5), finished_reservation=False, notified=False
    )

    for reservation in upcoming_reservations:
        user = reservation.player_reserving.user
        reservation.notified = True
        reservation.save()
        send_mail(
            subject='Poolhub Reservation Reminder',
            message=f'5 minutes before reservation {reservation.id}',
            from_email='luka.gurjidze04@gmail.com',
            recipient_list=[user.email],
            fail_silently=False  
        )



@shared_task
def start_game():
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=now() + timedelta(minutes=5), finished_reservation=False, notified=False
    )
    
    for reservation in upcoming_reservations:
        user = reservation.player_reserving.user
        reservation.notified = True
        reservation.save()
        send_mail(
            subject='Poolhub Reservation Reminder',
            message=f'5 minutes before reservation {reservation.id}',
            from_email='luka.gurjidze04@gmail.com',
            recipient_list=[user.email],
            fail_silently=False  
        )





