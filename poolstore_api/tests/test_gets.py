from django.urls import reverse
from rest_framework.test import APIClient
import pytest

from poolstore_api.views import PoolHouseViewSet

@pytest.mark.django_db
class TestStart:
    def setup_method(self, method):
        self.client = APIClient()

    def teardown_method(self, method):
        print('teardown')

    def test_poolhouses(self):
        url = reverse("poolhouse-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_players(self):
        url = reverse('player-list')
        response = self.client.get(url)
        assert response.status_code == 200

    