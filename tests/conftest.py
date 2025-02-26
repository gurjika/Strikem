import pytest
from datetime import time
from core.models import User
from poolstore.models import PoolHouse, PoolHouseStaff


@pytest.fixture
def test_poolhouse():
    close_time = time(10, 0)

    return PoolHouse.objects.create(
        id=1,
        title='test-pool', 
        latitude=42.4, 
        longitude=42.2, 
        close_time=close_time, 
        open_time=close_time, 
        address='addresss'
    )

@pytest.fixture
def test_user():
    return User.objects.create(username='non-staff', email='sad@g.com')


@pytest.fixture
def test_user_second():
    return User.objects.create(username='leboswki', email='rug@g.com')


@pytest.fixture
def test_staff_user(test_poolhouse):
    user = User.objects.create(username='staff', email='staff@s.com', is_staff=True)
    PoolHouseStaff.objects.create(user=user, poolhouse=test_poolhouse)
    return user


@pytest.fixture
def in_memory_channel_layers(settings):
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
    yield