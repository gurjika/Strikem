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


@pytest_asyncio.fixture(scope='function')
async def communicator(user_a):
    communicator = WebsocketCommunicator(BaseNotificationConsumer.as_asgi(), f"/ws/base/")
    communicator.scope['user'] = user_a
    yield communicator
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_chat_matchup_ok(communicator):
    connected, _ = await communicator.connect(timeout=30)
    assert connected
    


# @pytest.mark.django_db
# @pytest.mark.asyncio
# async def test_chat_matchmake_send(communicator):
#     await communicator.connect(timeout=10)
#     message = {
#         'action': 'matchmake',
#         'protocol': 'initial',
#     }
    
#     await communicator.send_json_to(message)
#     response = await communicator.receive_json_from()
#     print(response)
#     assert response == message
