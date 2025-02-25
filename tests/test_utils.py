from unittest import TestCase   
from core.utils import generate_random_string, generate_username
import pytest

class TestUtils:

    def setup_method(self):
        pass
    

    def teardown_method(self):
        pass
    
    def test_generate_random_string(self):
        result = generate_random_string()
        assert len(result) == 7
        assert isinstance(result, str)
        
    def test_get_nearby_players(self):
        pass

    @pytest.mark.parametrize('email', [('admin@gmail.com'), ('t@mail.ru')])
    def test_generate_username(self, email):
        result = generate_username(email)
        assert result[-4:].isdigit()
    


