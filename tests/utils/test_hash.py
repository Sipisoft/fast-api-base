from src.utils.hash import Hash

def test_hash_encrypt_and_verify():
    password = "secret_password"
    hashed = Hash.encrypt(password)
    
    assert hashed != password
    assert Hash.verify(password, hashed) is True
    assert Hash.verify("wrong_password", hashed) is False

def test_generate_token():
    token1 = Hash.generate_token()
    token2 = Hash.generate_token()
    
    assert token1 != token2
    assert len(token1) > 32  # base64 encoded 32 bytes

def test_generate_api_key():
    key1 = Hash.generate_api_key()
    key2 = Hash.generate_api_key()
    
    assert key1 != key2
    assert len(key1) > 24
