from datetime import timezone
import time
import pytest
from channels.testing import WebsocketCommunicator
from poolstore.consumers import BaseNotificationConsumer
from core.models import User
from model_bakery import baker
from poolstore.models import Matchup, Message, Player
import pytest_asyncio
from unittest.mock import patch


@pytest.fixture
def user_a():
    user = User.objects.create(username='user_a', email='email@ss1.com')
    return user


@pytest.fixture
def user_b():
    user = User.objects.create(username='user_b', email='email@ss.com')
    return user


@pytest_asyncio.fixture
async def communicator_a(user_a):
    communicator = WebsocketCommunicator(BaseNotificationConsumer.as_asgi(), f"/ws/base/")
    communicator.scope['user'] = user_a
    connected, _ = await communicator.connect(timeout=30)
    assert connected
    yield communicator
    await communicator.disconnect()

# @pytest_asyncio.fixture
# async def communicator_b(user_b):
#     test_uuid = "test-uuidb"

#     # Create a WebSocket communicator for User B
#     # with patch("django.core.cache.cache.get", return_value=user_b.id):  # Mock cache
#     communicator = WebsocketCommunicator(BaseNotificationConsumer.as_asgi(), f"/ws/base/?uuid={test_uuid}")
#     communicator.scope['user'] = user_b

#     connected, _ = await communicator.connect(timeout=30)
#     assert connected
#     yield communicator
#     await communicator.disconnect()

@pytest.mark.skip(reason='Not Yet')
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_chat_message_send_receive(communicator_a, communicator_b, matchup, user_a):
    print(user_a.player)
    # User A sends a message
    await communicator_a.send_json_to({
        'action': 'base',
        'message': 'Hello, User B!',
        'username': 'user_a',
        'matchup_id': str(matchup.id),
        'sender_player_id': user_a.player.id,
    })

    # User B receives the message
    time.sleep(5)
    response = await communicator_b.receive_json_from()
    assert response == {
        'matchup_id': str(matchup.id),
        'message': 'Hello, User B!',
        'username': 'user_a',
        'protocol': 'handleMessage',
        'sub_protocol': None,  
        'time_sent': response['time_sent'], 
        'sender_player_id': 1,
        'update_message_count': False,
    }




@pytest.fixture
def matchup(user_a, user_b):
    # Create a test matchup
    return baker.make(Matchup, player_accepting=user_a.player, player_inviting=user_b.player)


@pytest.fixture
def message(matchup, player):
    # Create a test message
    return baker.make(Message, body='Hello, User B!', matchup=matchup )

