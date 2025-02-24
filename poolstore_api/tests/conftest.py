import pytest
from datetime import time
from poolstore.models import PoolHouse


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