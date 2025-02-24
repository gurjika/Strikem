from unittest import TestCase   
from core.utils import generate_random_string

class TestUtils(TestCase):

    def setUp(self):
        return super().setUp()
    

    def tearDown(self):
        return super().tearDown()
    

    def test_generate_random_string(self):
        string = generate_random_string()
        assert len(string) == 7