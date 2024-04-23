import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from .models import Invitation, MatchMake, Matchup, Player
from channels.db import database_sync_to_async

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
        text_data_json = json.loads(text_data)
        changed = text_data_json['changed']


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_table',
                'changed': changed
            }
        )

    async def update_table(self, event):

        changed = event['changed']

        await self.send(text_data=json.dumps(
            {
                'changed': changed
            }
        ))

class MatchMakeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.GROUP_NAME = 'matchmake'
        self.room_name_for_specific_user = f"user_{self.scope['user'].username}"


        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )


        await self.channel_layer.group_add(
            self.room_name_for_specific_user,
            self.channel_name
        )
        

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.room_name_for_specific_user,
            self.channel_name
        )


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        username = text_data_json['username']
        matchmaker_username = text_data_json.get('matchmaker_username')
        invite_response = text_data_json.get('invite_response')
       

        player = await database_sync_to_async(Player.objects.get)(user__username=username)

        if invite_response:
            invite_sender_username = text_data_json['invite_sender_username']
            if invite_response == 'accept':
                # IF PLAYER ACCEPTS CREATE MATCHUP AND REMOVE THE PLAYER FROM THE INVITING PLAYERS' LIST
                accepter_player = await database_sync_to_async(Player.objects.get)(user__username=username)
                inviter_player = await database_sync_to_async(Player.objects.get)(user__username=invite_sender_username)

                match_make_instance = await database_sync_to_async(MatchMake.objects.get)(player=accepter_player)

                accepter_player.inviting_to_play = False
                await database_sync_to_async(accepter_player.save)()

                await database_sync_to_async(match_make_instance.delete)()

                mathup_object = await database_sync_to_async(Matchup.objects.create)(player_accepting=accepter_player, player_inviting=inviter_player)

                
                # SENDING ACCEPTING NOTIFICATION TO THE SENDER

                await self.channel_layer.group_send(
                    f'user_{invite_sender_username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'username': username,
                        'matchup_id': mathup_object.id
                    }
                )


                # SENDING ACCEPTING NOTIFICATION TO THE ACCEPTER

                await self.channel_layer.group_send(
                    f'user_{username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'username': username,
                        'matchup_id': mathup_object.id,
                        'sub_protocol': 'accepter'
                    }
                )
            # SENDING NOTIFICATION ONLY TO THE DENIED PLAYER
            elif invite_response == 'deny':
                await self.channel_layer.group_send(
                    f'user_{invite_sender_username}',
                    {
                        'type': 'handle_invite_response',
                        'invite_response': invite_response,
                        'invite_sender_username': invite_sender_username,
                        'username': username,
                    }
                )
            
            

        elif matchmaker_username:
            player_inviting = player
            player_invited = await database_sync_to_async(Player.objects.get)(user__username=matchmaker_username)

            await database_sync_to_async(Invitation.objects.create)(player_inviting=player_inviting, player_invited=player_invited)

            await self.channel_layer.group_send(
                f'user_{matchmaker_username}',
                {
                    'type': 'display_invite',
                    'invite_sender_username': username
                }
            )


            
            

        elif not player.inviting_to_play:


            player.inviting_to_play = True
            await database_sync_to_async(player.save)()

            await database_sync_to_async(MatchMake.objects.create)(player=player)


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

            match_make_instance = await database_sync_to_async(MatchMake.objects.get)(player=player)

            await database_sync_to_async(match_make_instance.delete)()

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

    async def display_invite(self, event):
        invite_sender_username = event['invite_sender_username']

        await self.send(text_data=json.dumps(
            {
                'inviteSenderUsername': invite_sender_username,
                'protocol': 'invited',
            }
        ))


    async def handle_invite_response(self, event):
        username = event['username']
        response = event['invite_response']
        invite_sender_username = event['invite_sender_username']
        sub_protocol = event.get('sub_protocol')
        matchup_id = event.get('matchup_id')

        if response == 'accept':


            await self.send(text_data=json.dumps(
                {   
                    'invite_response': 'ACCEPTED',
                    'accepterUsername': username,
                    'inviteSenderUsername': invite_sender_username,
                    'protocol': 'handling_invite_response',
                    'sub_protocol': sub_protocol,
                    'matchup_id': matchup_id
                }, default=str #FOR UUID SERIALIZATION ISSUES
            ))

        elif response == 'deny':
            await self.send(text_data=json.dumps(
                {   
                    'invite_response': 'DENIED',
                    'accepterUsername': username,
                    'protocol': 'handling_invite_response'
                }
            ))


    async def accepting_player_cleanup(self, event):

        await self.send(text_data=json.dumps(
            {
                'protocol': 'accepter_player_cleanup',
                'username': event['accepter_username']
            }
        ))






        
class MatchupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        matchup_id = self.scope['url_route']['kwargs']['matchup_id']
        self.GROUP_NAME = f'matchup_{matchup_id}'


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



        self.accept()
        
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        username = text_data_json['username']

        

        self.channel_layer.group_send(
            self.GROUP_NAME, 
            {
                'type': 'handle_user_joined',
                'username': username
            }
        )

    async def handle_user_joined(self, event):
        username = event['username']
        await self.send(json.dumps(
            {
                'username': username,
            }
        ))
    

