import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Invitation, InvitationDenied, Matchup, Notification, Player, Message
from channels.db import database_sync_to_async
from datetime import timedelta
import datetime
from .tasks import delete_denied_invite
from poolstore.tasks import invitation_cleanup 
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
        print('action: ', text_data_json.get('action'))
        print('protocol: ', text_data_json.get('protocol'))
        print('payload: ', text_data_json)

        action = text_data_json.get('action')

        

        if action == 'matchup':
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

            else:

                await self.matchup(text_data_json)


        elif action == 'change_matchup':
            matchup_id = text_data_json.get('matchup_id')
            cache.delete(f'{self.user.username}_{matchup_id}')
            self.matchup_state = matchup_id


        elif action == self.matchmake_room_name:
            self.matchup_state = ''

            self.current = self.matchmake_room_name
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
            self.matchup_state = ''

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
            self.matchup_state = ''

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
        

        print(f'matchup state for user {self.user.username}', self.matchup_state)
        print(matchup_id)
        update_message_count = False

        if self.matchup_state != matchup_id:
            update_message_count = await self.update_matchup_read(matchup_id)



        await self.send(text_data=json.dumps(
            {
                'matchup_id': matchup_id,
                'message': message,
                'username': username,
                'protocol': 'handleMessage',
                'sub_protocol': sub_protocol,
                'time_sent': time_sent,
                'sender_player_id': sender_player_id,
                'update_message_count': update_message_count
         }, default=str))


    @database_sync_to_async
    def update_matchup_read(self, matchup_id):
        already_notified = cache.get(f'{self.user.username}_{matchup_id}')

        if not already_notified:
            matchup = Matchup.objects.get(id=matchup_id)

            if matchup.read:
                matchup.read = False
                matchup.save()

                cache.set(f'{self.user.username}_{matchup_id}', True, timeout=600)
                print('cache did not work')
                return True
            
        print('used cache')
        return False

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
                'protocol': 'finish session',
                'game_session_id': event['game_session_id']

            }
        ))

    async def matchup(self, text_data=None, bytes_data=None):
        text_data_json = text_data
        self.opponent_username = text_data_json.get('opponent_username')
        username = text_data_json.get('username')
        message = text_data_json.get('message')
        # user_state = text_data_json.get('user_state')
        # protocol = text_data_json.get('protocol')

        player = await database_sync_to_async(Player.objects.get)(user=self.user)

        # if protocol == 'acknowledge':
        #     active_user_username = text_data_json['active_user']
        #     await self.channel_layer.group_send(
        #         f'user_{active_user_username}',
        #         {
                    
        #             'type': 'handle_acknowledge',
        #             'active_user': self.user.username
        #         },
        #     )

        # if user_state:
        #     opponents = await database_sync_to_async(list)(player.get_opponents())
                
        #     for opponent in opponents:
        #         await self.channel_layer.group_send(
        #             f'user_{opponent.user.username}', 
        #             {
        #                 'type': 'handle_user_state',
        #                 'username': self.user.username,
        #                 'user_state': 'joined'
        #             }
        #         )


       
        if message:
            
            matchup_id = text_data_json['matchup_id']

            
            last_message = await database_sync_to_async(Message.objects.filter(matchup_id=matchup_id).last)()
            new_message = await database_sync_to_async(Message.objects.create)(matchup_id=matchup_id, body=message, sender=player)

            print(f'on message opponent is {self.opponent_username}')
            print('matchup_id on message: ', matchup_id)

            is_outdated = False

            try:
                time_difference = new_message.time_sent - last_message.time_sent
                if time_difference > timedelta(minutes=20):
                    is_outdated = True
                
            except AttributeError:
                pass

            formatted_datetime = new_message.time_sent.strftime('%b %#d, %I:%M %p')

            message_json = {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'sender_player_id': player.id,
                'time_sent': formatted_datetime,
                'matchup_id': matchup_id,
                'update_message_count': False
            }




            if is_outdated or last_message is None:
                message_json['sub_protocol'] = 'last_message_outdated'
                new_message.after_outdated = True
                await database_sync_to_async(new_message.save)()

                await self.channel_layer.group_send(
                    f'user_{self.opponent_username}',
                    message_json
                )



            else:
                await self.channel_layer.group_send(
                    f'user_{self.opponent_username}',
                    message_json
                )


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

        print(event)
        data = {
            'changed_table_local_id': event['local_table_id'],
            'changed_table_id': event['table_id'],
            'game_session_id': event['game_session_id'],
            'protocol': protocol,
        }

        if protocol == 'now_busy':

            busy_data = {
                'player_reserving_username': event['player_reserving_username'],
                'player_reserving_profile_picture': event['player_reserving_profile_picture'],
                'player_reserving_id': event['player_reserving_id'],
                'other_player_username': event.get('other_player_username'),
                'other_player_profile': event.get('other_player_profile'),
                'other_player_id': event.get('other_player_id'),
                'start_time': event['start_time'],
                'duration': event['duration']
            }
            data.update(busy_data)

        await self.send(text_data=json.dumps(data))
        


















  


