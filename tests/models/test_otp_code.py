import pytest
from datetime import datetime, timedelta
import uuid
from src.models.otp_code import OtpCode, OtpPurpose

def test_otp_code_is_expired():
    now = datetime.utcnow()
    otp = OtpCode(expires_at=now - timedelta(minutes=1))
    assert otp.is_expired(now) is True
    
    otp2 = OtpCode(expires_at=now + timedelta(minutes=1))
    assert otp2.is_expired(now) is False

def test_otp_code_is_locked():
    now = datetime.utcnow()
    otp = OtpCode(locked_until=now + timedelta(minutes=10))
    assert otp.is_locked(now) is True
    
    otp2 = OtpCode(locked_until=now - timedelta(minutes=10))
    assert otp2.is_locked(now) is False
    
    otp3 = OtpCode(locked_until=None)
    assert otp3.is_locked(now) is False

def test_register_failed_attempt():
    now = datetime.utcnow()
    otp = OtpCode(attempts=0, max_attempts=3)
    
    otp.register_failed_attempt(now, 10)
    assert otp.attempts == 1
    assert otp.locked_until is None
    
    otp.register_failed_attempt(now, 10)
    assert otp.attempts == 2
    
    otp.register_failed_attempt(now, 10)
    assert otp.attempts == 3
    assert otp.locked_until == now + timedelta(minutes=10)

def test_mark_used():
    now = datetime.utcnow()
    otp = OtpCode(active=True, used_at=None)
    
    otp.mark_used(now)
    assert otp.active is False
    assert otp.used_at == now

def test_otp_defaults():
    otp = OtpCode()
    assert otp.purpose is None
