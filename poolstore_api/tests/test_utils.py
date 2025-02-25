from unittest import TestCase   
from core.utils import generate_random_string, generate_username
import pytest

class TestUtils(TestCase):

    def setUp(self):
        return super().setUp()
    

    def tearDown(self):
        return super().tearDown()
    

    def test_generate_random_string(self):
        result = generate_random_string()
        assert len(result) == 7
        assert isinstance(result, str)\
        
    def test_get_nearby_players(self):
        pass



