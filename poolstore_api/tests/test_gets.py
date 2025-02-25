from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from core.models import User
from poolstore.models import PoolHouse, PoolTable
from poolstore_api.views import PoolHouseViewSet
from model_bakery import baker

@pytest.mark.django_db
class TestStart:
    def setup_method(self, method):
        self.client = APIClient()

    def teardown_method(self, method):
        pass

    def test_poolhouses_200(self):
        url = reverse("poolhouse-list")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_players_200(self):
        url = reverse('player-list')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_history_no_auth_200(self, test_user):
        url = reverse('history-list', kwargs={'player_pk': test_user.player.id})
        response = self.client.get(url)
        assert response.status_code == 200

    def test_game_session_non_staff_403(self, test_user):
        url = reverse('game-session-list', kwargs={'poolhouse_pk': 1})
        self.client.force_authenticate(user=test_user)
        response = self.client.get(url)
        assert response.status_code == 403

    def test_game_session_staff_200(self, test_staff_user, test_poolhouse):
        url = reverse('game-session-list', kwargs={'poolhouse_pk': test_poolhouse.id})
        self.client.force_authenticate(user=test_staff_user)
        response = self.client.get(url)
        assert response.status_code == 200

    def test_game_session_other_staff_403(self, test_staff_user):
        other_poolhouse = baker.make(PoolHouse, slug='other-poolhouse')
        url = reverse('game-session-list', kwargs={'poolhouse_pk': other_poolhouse.id})
        self.client.force_authenticate(user=test_staff_user)
        response = self.client.get(url)
        assert response.status_code == 403

    def test_matchmake_no_auth_401(self):
        url = reverse('matchmake-list')
        response = self.client.get(url)
        assert response.status_code == 401

    def test_matchup_auth_200(self, test_user):
        url = reverse('matchup-list')
        self.client.force_authenticate(user=test_user)
        response = self.client.get(url)
        assert response.status_code == 200

    def test_matchmake_auth_200(self, test_user):
        url = reverse('matchmake-list')
        self.client.force_authenticate(user=test_user)
        response = self.client.get(url)
        assert response.status_code == 200

    def test_notification_auth_200(self, test_user):
        url = reverse('notification-list')
        self.client.force_authenticate(user=test_user)
        response = self.client.get(url)
        assert response.status_code == 200

    def test_notification_no_auth_401(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        assert response.status_code == 401

    def test_matchup_no_auth_401(self):
        url = reverse('matchup-list')
        response = self.client.get(url)
        assert response.status_code == 401

    def test_rating_no_auth_200(self, test_poolhouse):
        url = reverse('rating-list', kwargs={'poolhouse_pk': test_poolhouse.id})
        response = self.client.get(url)
        assert response.status_code == 200


    def test_reservations_no_auth_200(self, test_poolhouse):
        table = baker.make(PoolTable, poolhouse=test_poolhouse)
        url = reverse('table-reserve', kwargs={'poolhouse_pk': test_poolhouse.id, 'pk': table.id})
        response = self.client.get(f'{url}?date=2025-02-25')
        assert response.status_code == 200

    @pytest.mark.parametrize('rating', [(1), (2), (3), (4), (5)])
    def test_rating_no_auth_200(self, rating, test_poolhouse):
        url = reverse('filter-rating', kwargs={'poolhouse_pk': test_poolhouse.id})
        response = self.client.get(f'{url}?filter={rating}')
        assert response.status_code == 200
