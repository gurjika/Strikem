import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from django.db.models import Q
from core.models import User
from .models import Invitation, InvitationDenied, MatchMake, Matchup, Notification, Player, Message
from channels.db import database_sync_to_async
from datetime import timedelta
import datetime
from .tasks import delete_denied_invite
from poolstore_api.tasks import invitation_cleanup 
from .models import NotificationChoices
from datetime import datetime, timezone
from django.core.cache import cache




class BaseNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poolhouse_room_name = 'none'
        self.matchmake_room_name = 'matchmake'
        self.current = ''
        self.user = self.scope['user']
        self.room_name_for_specific_user = f"user_{self.user.username}"


        await self.channel_layer.group_add(
            self.room_name_for_specific_user,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code=None):
   

        await self.channel_layer.group_discard(
            self.room_name_for_specific_user,
            self.channel_name
        )




    async def receive(self, text_data=None, bytes_data=None):



        text_data_json = json.loads(text_data)
        print(text_data_json)
        print(text_data_json.get('action'))
        print(text_data_json.get('protocol'))


        action = text_data_json.get('action')

        

        if action == 'matchup':
            print('test poolhouse in matchup', self.poolhouse_room_name)
            self.current = 'matchup'


            if text_data_json.get('protocol') == 'initial':

                
                await self.channel_layer.group_discard(
                    self.matchmake_room_name,
                    self.channel_name
                )

                await self.channel_layer.group_discard(
                    self.poolhouse_room_name,
                    self.channel_name,
                )

                print('1: matchup',self.poolhouse_room_name)
            else:

                print('2: matchup',self.poolhouse_room_name)
                await self.matchup(text_data_json)


        elif action == 'change_matchup':
            matchup_id = text_data_json.get('matchup_id')
            cache.set(f'matchup_{self.user.username}', f'{matchup_id}', timeout=600)


        elif action == self.matchmake_room_name:
            self.current = self.matchmake_room_name
            cache.delete(f'matchup_{self.user.username}')
            if text_data_json.get('protocol') == 'initial':
                

                await self.channel_layer.group_discard(
                    self.poolhouse_room_name,
                    self.channel_name,
                )


                await self.channel_layer.group_add(
                    self.matchmake_room_name,
                    self.channel_name
                )


            else:
                await self.matchmake(text_data_json)


        elif action == 'poolhouse':
            cache.delete(f'matchup_{self.user.username}')

            poolhouse_name = text_data_json.get('poolhouseName')
            self.poolhouse_room_name = f'poolhouse_{poolhouse_name}'
            self.current = self.poolhouse_room_name

            await self.channel_layer.group_discard(
                self.matchmake_room_name,
                self.channel_name
            )

            await self.channel_layer.group_add(
                self.poolhouse_room_name,
                self.channel_name
            )

            print('poolhouse', self.poolhouse_room_name)


        elif action == 'base':
            cache.delete(f'matchup_{self.user.username}')

            self.current = 'base'
            await self.channel_layer.group_discard(
                self.matchmake_room_name,
                self.channel_name
            )

            await self.channel_layer.group_discard(
                self.poolhouse_room_name,
                self.channel_name
            )












    async def display_invite(self, event):
        invite_sender_username = event['invite_sender_username']
        inviter_profile_image = event.get('inviter_profile_image')


        await self.send(text_data=json.dumps(
            {
                'inviteSenderUsername': invite_sender_username,
                'protocol': 'invited',
                'inviter_profile_image': inviter_profile_image,
            }
        ))


    async def handle_invite_response(self, event):
        username = event['username']
        response = event['invite_response']
        invite_sender_username = event['invite_sender_username']
        sub_protocol = event.get('sub_protocol')
        matchup_id = event.get('matchup_id')
        profile_image_url = event.get('responder_profile_image')
        invite_sender_profile_pic = event.get('invite_sender_profile_pic') 


        if response == 'accept':


            await self.send(text_data=json.dumps(
                {   
                    'invite_response': 'ACCEPTED',
                    'accepterUsername': username,
                    'inviteSenderUsername': invite_sender_username,
                    'protocol': 'handling_invite_response',
                    'sub_protocol': sub_protocol,
                    'matchup_id': matchup_id,
                    'responder_profile_image': profile_image_url,
                    'invite_sender_profile_pic': invite_sender_profile_pic,
                }, default=str #FOR UUID SERIALIZATION ISSUES
            ))

        elif response == 'deny':
            await self.send(text_data=json.dumps(
                {   
                    'invite_response': 'DENIED',
                    'accepterUsername': username,
                    'protocol': 'handling_invite_response',
                    'responder_profile_image': profile_image_url,
                }
            ))


    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        sub_protocol = event.get('sub_protocol')
        time_sent = event.get('time_sent')
        matchup_id = event['matchup_id']
        sender_player_id = event['sender_player_id']
        
        await self.send(text_data=json.dumps(
            {
                'matchup_id': matchup_id,
                'message': message,
                'username': username,
                'protocol': 'handleMessage',
                'sub_protocol': sub_protocol,
                'time_sent': time_sent,
                'sender_player_id': sender_player_id,
        }, default=str))


    async def handle_user_state(self, event):
        username = event['username']
        user_state = event['user_state']
        await self.send(json.dumps(
            {
                'username': username,
                'protocol': 'handleUserState',
                'user_state': user_state,
            }, default=str
        ))
 
    async def handle_acknowledge(self, event):
        
        await self.send(json.dumps(
            {   
                'username': event['active_user'],
                'protocol': 'handleAcknowledge',
            }, default=str
        ))

    async def finish_game_session(self, event):

        await self.send(json.dumps(
            {
                'protocol': 'finish session'
            }
        ))

    async def matchup(self, text_data=None, bytes_data=None):
        text_data_json = text_data
        self.opponent_username = text_data_json.get('opponent_username')
        username = text_data_json.get('username')
        message = text_data_json.get('message')
        user_state = text_data_json.get('user_state')
        protocol = text_data_json.get('protocol')

        player = await database_sync_to_async(Player.objects.get)(user=self.user)

        if protocol == 'acknowledge':
            active_user_username = text_data_json['active_user']
            await self.channel_layer.group_send(
                f'user_{active_user_username}',
                {
                    
                    'type': 'handle_acknowledge',
                    'active_user': self.user.username
                },
            )

        if user_state:
            opponents = await database_sync_to_async(list)(player.get_opponents())
                
            for opponent in opponents:
                await self.channel_layer.group_send(
                    f'user_{opponent.user.username}', 
                    {
                        'type': 'handle_user_state',
                        'username': self.user.username,
                        'user_state': 'joined'
                    }
                )


       
        elif message:
            
            matchup_id = text_data_json['matchup_id']

            
            last_message = await database_sync_to_async(Message.objects.filter(matchup_id=matchup_id).last)()
            new_message = await database_sync_to_async(Message.objects.create)(matchup_id=matchup_id, body=message, sender=player)

            print(cache.get(f'matchup_{self.opponent_username}'))
            print(matchup_id)
            print(matchup_id == cache.get(f'matchup_{self.opponent_username}'))

            if not matchup_id == cache.get(f'matchup_{self.opponent_username}'):
                matchup_read = cache.get(f'{matchup_id}_reading')
                print('cache did not work 1')
                if not matchup_read:
                    matchup = await database_sync_to_async(Matchup.objects.get)(id=matchup_id)
                    matchup.read = False
                    print('cache did not work 2')
                    await database_sync_to_async(matchup.save)()
                    cache.set(f'{matchup.id}_reading', 'read', timeout=300)

            is_outdated = False

            try:
                time_difference = new_message.time_sent - last_message.time_sent
                if time_difference > timedelta(minutes=20):
                    is_outdated = True
                
            except AttributeError:
                pass

            formatted_datetime = new_message.time_sent.strftime('%b %#d, %I:%M %p')
            if is_outdated or last_message is None:

                new_message.after_outdated = True
                await database_sync_to_async(new_message.save)()

                await self.channel_layer.group_send(
                    f'user_{self.opponent_username}',
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                        'sender_player_id': player.id,
                        'time_sent': formatted_datetime,
                        'matchup_id': matchup_id,
                        'sub_protocol': 'last_message_outdated',
                    }
                )


                await self.channel_layer.group_send(
                    f'user_{username}',
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': username,
                        'sender_player_id': player.id,
                        'time_sent': formatted_datetime,
                        'matchup_id': matchup_id,
                        'sub_protocol': 'last_message_outdated',
                    }
                )
            else:
                await self.channel_layer.group_send(
                    f'user_{self.opponent_username}',
                    {
                        'type': 'chat_message',
                        'message': message,
                        'matchup_id': matchup_id,
                        'username': username,
                        'sender_player_id': player.id,
                        'time_sent': formatted_datetime,
                    }
                )
                   
                # await self.channel_layer.group_send(
                #     f'user_{username}',
                #     {
                #         'type': 'chat_message',
                #         'message': message,
                #         'matchup_id': matchup_id,
                #         'username': username,
                #     }
                # )

    async def matchmake(self, text_data=None, bytes_data=None):

        self.GROUP_NAME = 'matchmake'

        text_data_json = text_data

        username = text_data_json.get('username')
        
        matchmaker_username = text_data_json.get('matchmaker_username')
        invite_response = text_data_json.get('invite_response')
        control_user = text_data_json.get('protocol')
        
        player = await database_sync_to_async(Player.objects.get)(user__username=username)

        if invite_response:
            invite_sender_username = text_data_json['invite_sender_username']

            response_player = await database_sync_to_async(Player.objects.get)(user__username=username)
            inviter_player = await database_sync_to_async(Player.objects.get)(user__username=invite_sender_username)
            if invite_response == 'accept':


                # IF PLAYER ACCEPTS CREATE MATCHUP AND REMOVE THE PLAYER FROM THE INVITING PLAYERS' LIST



                # match_make_instance_accepter = await database_sync_to_async(MatchMake.objects.get)(player=response_player)
                
                # try:
                #     match_make_instance_inviter = await database_sync_to_async(MatchMake.objects.get)(player=inviter_player)
                #     await database_sync_to_async(match_make_instance_inviter.delete)()
                # except MatchMake.DoesNotExist:
                #     pass
                
                # invitations = await database_sync_to_async(Invitation.objects.filter)(Q(player_inviting=response_player, player_invited=inviter_player) |Q(player_inviting=inviter_player, player_invited=response_player))





                invitation_cleanup.apply_async((response_player.id, inviter_player.id))
   
                # create_notification.apply_async((invite_sender_username, 'invitation', ), eta=start_time, task_id=f'custom_task_id_{obj.id}')
                

                response_player.inviting_to_play = False
                await database_sync_to_async(response_player.save)()
                inviter_player.inviting_to_play = False
                await database_sync_to_async(inviter_player.save)()

                # await database_sync_to_async(match_make_instance_accepter.delete)()
                

                mathup_object = await database_sync_to_async(Matchup.objects.create)(player_accepting=response_player, player_inviting=inviter_player)
                
                # SENDING ACCEPTING NOTIFICATION TO THE SENDER

                await self.create_notification(player=invite_sender_username, sent_by=username, type=NotificationChoices.ACCEPTED, body=f'{username} accepted your invite', extra=None)

                await self.channel_layer.group_send(
                    f'user_{invite_sender_username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'invite_sender_profile_pic': inviter_player.profile_image.url,
                        'responder_profile_image': response_player.profile_image.url,
                        'username': username,
                        'matchup_id': str(mathup_object.id)
                    }
                )


                # SENDING ACCEPTING NOTIFICATION TO THE ACCEPTER

                await self.channel_layer.group_send(
                    f'user_{username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'invite_sender_profile_pic': inviter_player.profile_image.url,
                        'responder_profile_image': response_player.profile_image.url,
                        'username': username,
                        'matchup_id': str(mathup_object.id),
                        'sub_protocol': 'accepter'
                    }
                )

            # SENDING NOTIFICATION ONLY TO THE DENIED PLAYER
            elif invite_response == 'deny':

                invitation = await database_sync_to_async(Invitation.objects.get)(player_inviting=inviter_player, player_invited=response_player)

                await database_sync_to_async(invitation.delete)()

                invitation_denied = await database_sync_to_async(InvitationDenied.objects.create)(player_invited=response_player, player_denied=inviter_player)
                current_utc = datetime.now(timezone.utc)

                delete_denied_invite.apply_async((invitation_denied.id,), eta=current_utc + timedelta(seconds=3))
                await self.create_notification(player=invite_sender_username, sent_by=username, type=NotificationChoices.REJECTED, body=None, extra=None)

                

                ## TODO SEND PCITURE WITH I`NVITATION
                

                await self.channel_layer.group_send(
                    f'user_{invite_sender_username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'responder_profile_image': response_player.profile_image.url,
                        'username': username,
                    }
                )
            
            
        elif matchmaker_username:
            player_inviting = player
            player_invited = await database_sync_to_async(Player.objects.get)(user__username=matchmaker_username)

            invitation_instance = await database_sync_to_async(Invitation.objects.create)(player_inviting=player_inviting, player_invited=player_invited)
            await self.create_notification(player=matchmaker_username, sent_by=username, type=NotificationChoices.INVITED, body=None, extra=None)


            await self.channel_layer.group_send(
                f'user_{matchmaker_username}',
                {
                    'type': 'display_invite',
                    'invite_sender_username': username,
                    'invitationId': invitation_instance.id,
                    'inviter_profile_image': player_inviting.profile_image.url
                }
            )


            
            

        if control_user:
            if not player.inviting_to_play:


                player.inviting_to_play = True
                await database_sync_to_async(player.save)()

                # await database_sync_to_async(MatchMake.objects.create)(player=player)


                await self.channel_layer.group_send(
                    self.GROUP_NAME,
                    {
                        'type': 'control_user',
                        'username': username,
                        'protocol': 'add'
                    }
                )

            elif player.inviting_to_play:

                player.inviting_to_play = False
                await database_sync_to_async(player.save)()

                # match_make_instance = await database_sync_to_async(MatchMake.objects.get)(player=player)

                # await database_sync_to_async(match_make_instance.delete)()

                player_invitations = await database_sync_to_async(Invitation.objects.filter)(player_invited=player)

                await database_sync_to_async(player_invitations.delete)()


                await self.channel_layer.group_send(
                    self.GROUP_NAME,
                    {
                        'type': 'control_user',
                        'username': username,
                        'protocol': 'delete'
                    }
                ) 




    async def control_user(self, event):


        username = event['username']
        protocol = event['protocol']

        # FOR HTMX 
        # html = get_template('poolstore/partials/matchmakers.html').render(
        #     context={'username': username}
        # )
        # await self.send(text_data=html)

        await self.send(text_data=json.dumps(
            {
                'username': username,
                'protocol': protocol
            }
        ))

    async def create_notification(self, player, sent_by, type, body=None, extra=None):
        player = await database_sync_to_async(Player.objects.get)(user__username=player)
        
        if sent_by:
            sent_by = await database_sync_to_async(Player.objects.get)(user__username=sent_by)

        await database_sync_to_async (Notification.objects.create)(
            player=player,
            body=body,
            sent_by=sent_by,
            extra=extra,
            type=type,
        )
        
        # if type == 'MSG':
        #     last_message = Notification.objects.filter(player=player, type='MSG').order_by('-timestamp').first()
            
        #     if last_message:
        #         last_message.delete()





    async def accepting_player_cleanup(self, event):


        await self.send(text_data=json.dumps(
            {
                'protocol': 'accepter_player_cleanup',
                'accepter_username': event['accepter_username'],
                'inviter_username': event['inviter_username']
            }
        ))
    
    async def update_table(self, event):
        protocol = event['protocol']
        data = {
            'changed_table_local_id': event['local_table_id'],
            'changed_table_id': event['table_id'],
            'game_session_id': event['game_session_id'],
            'protocol': protocol
        }

        if protocol == 'now_busy':

            busy_data = {
                'player_reserving_username': event['player_reserving_username'],
                'player_reserving_profile_picture': event['player_reserving_profile_picture'],
                'player_reserving_id': event['player_reserving_id'],
                'other_player_username': event.get('other_player_username'),
                'other_player_profile': event.get('other_player_profile'),
                'other_player_id': event.get('other_player_id')
            }
            data.update(busy_data)

        await self.send(text_data=json.dumps(data))
        

            




 


class PoolhouseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['poolhouse']
        self.room_group_name = f'poolhouse_{self.room_name}'


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )


      
        await self.accept()


    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        pass











class MatchMakeConsumer(BaseNotificationConsumer):
    async def connect(self):
        await super().connect()
        self.GROUP_NAME = 'matchmake'


        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )




    async def disconnect(self, code):
        await super().disconnect()
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )



    async def receive(self, text_data=None, bytes_data=None):
        pass
       













        
# class MatchupConsumer(BaseNotificationConsumer):
#     async def connect(self):
#         await super().connect()


#         self.opponent_username = ''

        
#         await self.accept()

#     async def disconnect(self, code):

#         player = await database_sync_to_async(Player.objects.get)(user=self.user)
#         opponents = await database_sync_to_async(list)(player.get_opponents())
                    
#         # TODO PUT THIS IN CELERY TASK
#         for opponent in opponents:
#             await self.channel_layer.group_send(
#                 f'user_{opponent.user.username}', 
#                 {
#                     'type': 'handle_user_state',
#                     'username': self.user.username,
#                     'user_state': 'left'
#                 }
#             )
#         await super().disconnect()

 
    










    
class GameSessionConsumer(BaseNotificationConsumer):
    async def connect(self):
  
        self.user = self.scope['user']
        session_id = self.scope['url_route']['kwargs']['session_id']
        self.GROUP_NAME = f'session_{session_id}'


        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )

        
        await self.accept()

    async def disconnect(self, code):

        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )
        
    
    async def receive(self, text_data=None, bytes_data=None):
        pass


    


  


