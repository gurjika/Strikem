import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from .models import MatchMake, Player
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
        text_data_json = json.loads(text_data)
        username = text_data_json['username']


        await self.channel_layer.group_send(
            self.GROUP_NAME,
            {
                'type': 'add_user',
                'username': username
            }
        )

    async def add_user(self, event):
        username = event['username']
        print(username)
        player = await database_sync_to_async(Player.objects.get)(user__username=username)

        await database_sync_to_async(MatchMake.objects.create)(player=player)

        # html = get_template('poolstore/partials/matchmakers.html').render(
        #     context={'username': username}
        # )

        await self.send(text_data=json.dumps(
            {
                'username': username
            }
        ))


        # await self.send(text_data=html)

        

    

