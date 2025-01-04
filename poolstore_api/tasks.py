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


# @shared_task
# def start_game_session(reservation_id):
#     reservation = Reservation.objects.get(id=reservation_id)
#     game_session = GameSession.objects.create(pooltable=reservation.table)

#     if reservation.other_player:
#         PlayerGameSession.objects.create(game_session=game_session, player=reservation.other_player)
    
#     PlayerGameSession.objects.create(game_session=game_session, player=reservation.player_reserving)
    
#     finish_game_session.apply_async((
#         game_session.id, reservation.id, 'Finished'), 
#         eta=reservation.end_time, 
#         task_id=f'game_session_{game_session.id}'
#     )
    

#     event = {
#         'type': 'update_table',
#         'table_id': reservation.table.table_id,
#         'protocol': 'now_busy'
#     }

#     channel_layer = get_channel_layer()
#     game_session.pooltable.free = False
#     game_session.save()

#     async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)




@shared_task
def finish_game_session():

    upcoming_reservations = Reservation.objects.filter(
        end_time__lte=now(), finished_reservation=False, in_process=True
    )
    print('Finishing game sessions: ', upcoming_reservations)
    for reservation in upcoming_reservations:
        game_session = GameSession.objects.get(pooltable=reservation.table, status_finished=False)
        reservation = Reservation.objects.get(id=reservation.id)
        channel_layer = get_channel_layer()
        
       
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
        # else:
        #     event = {
        #         'type': 'abort_game_session',
        #         'game_session_id': str(game_session.id),
        #     }

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




    

@shared_task
def send_email_before_res():
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=now() + timedelta(minutes=5), finished_reservation=False, notified=False
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
    upcoming_reservations = Reservation.objects.filter(
        start_time__lte=now(), finished_reservation=False, in_process=False,
    )
    
    print('Starting game sessions: ', upcoming_reservations)
    for reservation in upcoming_reservations:
        with transaction.atomic():
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
            
            # finish_game_session.apply_async((
            #     game_session.id, reservation.id, 'Finished'), 
            #     eta=reservation.end_time, 
            #     task_id=f'game_session_{game_session.id}'
            # )
            


            channel_layer = get_channel_layer()
            game_session.pooltable.free = False
            game_session.pooltable.save()
            game_session.save()
            reservation.in_process = True
            reservation.save()
            async_to_sync(channel_layer.group_send)(f'poolhouse_{reservation.table.poolhouse.slug}', event)






