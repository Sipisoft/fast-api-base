import pytest
from src.utils.password import generate_strong_password
import string

def test_generate_strong_password_length():
    password = generate_strong_password(12)
    assert len(password) == 12
    
    password_default = generate_strong_password()
    assert len(password_default) == 16

def test_generate_strong_password_content():
    password = generate_strong_password(20)
    
    # Check if it contains at least one of each required type
    assert any(c in string.ascii_lowercase for c in password)
    assert any(c in string.ascii_uppercase for c in password)
    assert any(c in string.digits for c in password)
    assert any(c in string.punctuation for c in password)

def test_generate_strong_password_uniqueness():
    p1 = generate_strong_password()
    p2 = generate_strong_password()
    assert p1 != p2

def test_generate_strong_password_too_short():
    with pytest.raises(ValueError, match="Password length must be at least 4 characters"):
        generate_strong_password(3)
