from datetime import timedelta
from celery import shared_task
from channels.layers import get_channel_layer
from poolstore.models import GameSession, Invitation, Notification, Player, PlayerGameSession, PoolTable, Reservation, NotificationChoices
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import localtime
from django.utils.timezone import now




User = get_user_model()


@shared_task
def start_game_session(reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    game_session = GameSession.objects.create(pooltable=reservation.table)

    start_time_formatted = localtime(reservation.start_time).isoformat()
    
    event = {
        'type': 'update_table',
        'local_table_id': reservation.table.table_id,
        'table_id': reservation.table.id,
        'protocol': 'now_busy',
        'game_session_id': str(game_session.id),
        'player_reserving_username': reservation.player_reserving.user.username,
        'player_reserving_profile_picture': reservation.player_reserving.profile_image.url,
        'player_reserving_id': reservation.player_reserving.id,
        'start_time': start_time_formatted,
        'duration': reservation.duration,
    }


    # event = {
    #     'type': 'update_table',
    #     'local_table_id': reservation.table.table_id,
    #     'table_id': reservation.table.id,
    #     'player_reserving_username': reservation.player_reserving.user.username,
    #     'player_reserving_profile': reservation.player_reserving.profile_image.url,
    #     'player_reserving_id': reservation.player_reserving.id,
    #     'other_player_username': reservation.other_player.user.username,
    #     'other_player_profile': reservation.other_player.profile_image.url,
    #     'other_player_id': reservation.other_player.id,
    #     'game_session_id': game_session.id,
    #     'protocol': 'now_free'
    # }

    if reservation.other_player:
        PlayerGameSession.objects.create(game_session=game_session, player=reservation.other_player)
        event['other_player_username'] = reservation.other_player.user.username
        event['other_player_profile'] = reservation.other_player.profile_image.url
        event['other_player_id'] = reservation.other_player.id

    PlayerGameSession.objects.create(game_session=game_session, player=reservation.player_reserving)
    
    finish_game_session.apply_async((
        game_session.id, reservation.id, 'Finished'), 
        eta=reservation.end_time, 
        task_id=f'game_session_{game_session.id}'
    )
    


    channel_layer = get_channel_layer()
    game_session.pooltable.free = False
    game_session.pooltable.save()
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
            'game_session_id': str(game_session.id),
        }

        Notification.objects.create(
            player=reservation.player_reserving,
            sent_by=None,
            body=None,
            extra=str(game_session.id),
            type=NotificationChoices.GAME_SESSION_END
        )
    else:
        event = {
            'type': 'abort_game_session',
            'game_session_id': str(game_session.id),
        }

    # for player in game_session.players.all():
    #     async_to_sync(channel_layer.group_send)(f'user_{player.user.username}', event)

    async_to_sync(channel_layer.group_send)(f'user_{reservation.player_reserving.user.username}', event)

    event = {
        'type': 'update_table',
        'local_table_id': reservation.table.table_id,
        'table_id': reservation.table.id,
        'game_session_id': str(game_session.id),
        'protocol': 'now_free'
    }

    async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)

    game_session.pooltable.free = True
    game_session.status_finished = True
    reservation.finished_reservation = True
    game_session.pooltable.save()
    reservation.save()
    game_session.save()




    

# @shared_task
# def send_email_before_res(user_id, res_id):
#     user = User.objects.get(id=user_id)

#     send_mail(
#         subject='Poolhub Reservation',
#         message=f'5 minutes before reservation {res_id}',
#         from_email='luka.gurjidze04@gmail.com',
#         recipient_list=[user.email],
#         fail_silently=False ## TESTING
#     )


@shared_task
def send_email_before_res():
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=now() + timedelta(minutes=5), finished_reservation=False,
    )
    for reservation in upcoming_reservations:
        user = reservation.player_reserving.user
        send_mail(
            subject='Poolhub Reservation Reminder',
            message=f'5 minutes before reservation {reservation.id}',
            from_email='luka.gurjidze04@gmail.com',
            recipient_list=[user.email],
            fail_silently=False  
        )



@shared_task
def invitation_cleanup(player_1, player_2):
    player_1 = Player.objects.get(id=player_1)
    player_2 = Player.objects.get(id=player_2)

    invitations = Invitation.objects.filter(
        Q(player_inviting=player_2, player_invited=player_1) |
        Q(player_inviting=player_1, player_invited=player_2)
    )

    invitations.delete()



