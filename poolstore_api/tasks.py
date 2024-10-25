from celery import shared_task
from channels.layers import get_channel_layer
from poolstore.models import GameSession, PlayerGameSession, PoolTable, Reservation
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


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
    


@shared_task
def finish_game_session(game_session_id, reservation_id, protocol):
    game_session = GameSession.objects.get(id=game_session_id)
    reservation = Reservation.objects.get(id=reservation_id)
    channel_layer = get_channel_layer()
    group_name = f'session_{game_session.id}'
    
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



    reservation.finished_reservation = True
    game_session.delete()
    reservation.save()




    

@shared_task
def send_email_before_res(user_id):
    user = User.objects.get(id=user_id)

    send_mail(
        subject='Poolhub Reservation',
        message='5 minutes before reservation',
        from_email='luka.gurjidze04@gmail.com',
        recipient_list=[user.email],
        fail_silently=False ## TESTING
    )



