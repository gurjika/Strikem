from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from poolstore.models import PoolHouse, PoolTable, Reservation
from model_bakery import baker
from datetime import datetime, timedelta
from django.utils import timezone

@pytest.mark.django_db
class TestPOST:
    def setup_method(self, method):
        self.client = APIClient()

    def teardown_method(self, method):
        pass

    def test_reserve_table_proper_200(self, test_user, test_poolhouse):
        table = baker.make(PoolTable, poolhouse=test_poolhouse)
        url = reverse('table-reserve', kwargs={'poolhouse_pk': test_poolhouse.id, 'pk': table.id})
        self.client.force_authenticate(user=test_user)
        response = self.client.post(url, data={'start_time': datetime.now(), 'duration': 30})
        assert response.status_code == 200


    def test_reserve_table_non_proper_between_ress_400(self, test_user, test_poolhouse):
        table = baker.make(PoolTable, poolhouse=test_poolhouse)
        start_time = timezone.now() - timedelta(minutes=30)
        end_time = timezone.now() + timedelta(minutes=30)
        real_end_datetime = timezone.now() + timedelta(minutes=35)
        Reservation.objects.create( \
            start_time=start_time,
            end_time=end_time,
            real_end_datetime=real_end_datetime,
            duration=60,
            table=table
        )

        url = reverse('table-reserve', kwargs={'poolhouse_pk': test_poolhouse.id, 'pk': table.id})
        self.client.force_authenticate(user=test_user)
        response = self.client.post(url, data={'start_time': datetime.now(), 'duration': 30})
        assert response.status_code == 400


    def test_reserve_table_proper_after_res_exact_200(self, test_user, test_poolhouse):
        table = baker.make(PoolTable, poolhouse=test_poolhouse)
        start_time = timezone.now() - timedelta(minutes=30)
        end_time = timezone.now() + timedelta(minutes=30)
        real_end_datetime = timezone.now() + timedelta(minutes=35)
        Reservation.objects.create( \
            start_time=start_time,
            end_time=end_time,
            real_end_datetime=real_end_datetime,
            duration=60,
            table=table
        )

        url = reverse('table-reserve', kwargs={'poolhouse_pk': test_poolhouse.id, 'pk': table.id})
        self.client.force_authenticate(user=test_user)
        response = self.client.post(url, data={'start_time': timezone.now() + timedelta(minutes=35), 'duration': 30})
        assert response.status_code == 200


    def test_reserve_table_proper_before_res_exact_200(self, test_user, test_poolhouse):
        table = baker.make(PoolTable, poolhouse=test_poolhouse)
        start_time = timezone.now() - timedelta(minutes=30)
        end_time = timezone.now() + timedelta(minutes=30)
        real_end_datetime = timezone.now() + timedelta(minutes=35)
        res_2_start = start_time - timedelta(minutes=35)
        
        Reservation.objects.create( \
            start_time=start_time,
            end_time=end_time,
            real_end_datetime=real_end_datetime,
            duration=60,
            table=table
        )

        url = reverse('table-reserve', kwargs={'poolhouse_pk': test_poolhouse.id, 'pk': table.id})
        self.client.force_authenticate(user=test_user)
        response = self.client.post(url, data={'start_time': res_2_start, 'duration': 30})
        assert response.status_code == 200