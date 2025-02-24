from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from core.models import User
from poolstore.models import PoolHouse
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

    # def test_history_401(self):
    #     url = reverse('history-list')
    #     response = self.client.get(url)
    #     assert response.status_code == 401

    def test_game_session_non_staff(self, test_poolhouse):
        url = reverse('game-session-list', kwargs={'poolhouse_pk': 1})
        user = User.objects.create(username='non-staff', email='sad@g.com')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        assert response.status_code == 403


    