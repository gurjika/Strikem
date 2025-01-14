from datetime import timedelta
from celery import shared_task
from channels.layers import get_channel_layer
from poolstore.models import GameSession, Notification, NotificationChoices, PlayerGameSession, PoolTable, Reservation
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.timezone import localtime
from django.db import transaction


User = get_user_model()






@shared_task
def finish_game_session():

    upcoming_reservations = Reservation.objects.filter(
        end_time__lte=now(), finished_reservation=False, in_process=True
    )
    print('Finishing game sessions: ', upcoming_reservations)
    for reservation in upcoming_reservations:
        game_session = GameSession.objects.get(pooltable=reservation.table, status_finished=False)
        channel_layer = get_channel_layer()
        
       
        event = {
            'type': 'finish_game_session',
            'game_session_id': str(game_session.id),
        }


        notification = Notification.objects.create(
            player=reservation.player_reserving,
            sent_by=None,
            body='Your game session has ended',
            extra=str(game_session.id),
            type=NotificationChoices.GAME_SESSION_END
        )
        
        if reservation.other_player:
            notification.body = f'Game session with {reservation.other_player.user.username} has ended'
            notification.save()


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
        reservation.in_process = False
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
        start_time__gt=now(),
        start_time__lte=now() + timedelta(minutes=15), finished_reservation=False, notified=False
    )
    
    print('Sending emails: ', upcoming_reservations)
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
def start_game_session():
    with transaction.atomic():
        upcoming_reservations = Reservation.objects.filter(
            start_time__lte=now(), finished_reservation=False, in_process=False,
        )
        
        print('Starting game sessions: ', upcoming_reservations)
        for reservation in upcoming_reservations:
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



                if reservation.other_player:
                    PlayerGameSession.objects.create(game_session=game_session, player=reservation.other_player)
                    event['other_player_username'] = reservation.other_player.user.username
                    event['other_player_profile'] = reservation.other_player.profile_image.url
                    event['other_player_id'] = reservation.other_player.id

                PlayerGameSession.objects.create(game_session=game_session, player=reservation.player_reserving)
                


                channel_layer = get_channel_layer()
                game_session.pooltable.free = False
                game_session.pooltable.save()
                game_session.save()
                reservation.in_process = True
                reservation.save()
                async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)






