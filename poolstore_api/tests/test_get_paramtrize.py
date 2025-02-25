import pytest
from core.utils import generate_username

@pytest.mark.parametrize('email', [('admin@gmail.com'), ('t@mail.ru')])
def test_generate_username(email):
    result = generate_username(email)
    assert result[-4:].isdigit()
    

