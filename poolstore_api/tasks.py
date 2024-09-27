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
    game_session = GameSession.objects.create(poolhouse=reservation.table.poolhouse, pooltable=reservation.table)

    if reservation.matchup:
        PlayerGameSession.objects.create(game_session=game_session, player=reservation.matchup.player_inviting)
        PlayerGameSession.objects.create(game_session=game_session, player=reservation.matchup.player_accepting)
    
    else:
        PlayerGameSession.objects.create(game_session=game_session, player=reservation.player)
    

    




@shared_task
def finish_game_session(game_session_id):
    game_session = GameSession.objects.get(id=game_session_id)
    channel_layer = get_channel_layer()
    group_name = f'session_{game_session.id}'
    
    event = {
        'type': 'finish_game_session',
    }

    async_to_sync(channel_layer.group_send)(group_name, event)
    game_session.status_finished = True


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



