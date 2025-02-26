from django.urls import reverse
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestPOST:
    def setup_method(self, method):
        self.client = APIClient()

    def teardown_method(self, method):
        pass

    def test_player_location_update_200(self, test_user):
        url = reverse('player-location')
        self.client.force_authenticate(user=test_user)
        response = self.client.put(url, data={'lat': 40.6892, 'lng': 74.0445})
        assert response.status_code == 200