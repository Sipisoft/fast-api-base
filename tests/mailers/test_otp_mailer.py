import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.mailers.otp_mailer import OTPMailer

class MockAdmin:
    def __init__(self, email: str, username: str):
        self.email = email
        self.username = username

@pytest.fixture
def mock_admin():
    return MockAdmin(email="admin@example.com", username="adminuser")

@pytest.mark.anyio
@patch("src.mailers.base_mailer.FastMail")
@patch("src.mailers.base_mailer.ConnectionConfig")
async def test_otp_mailer_send_success(mock_conf, mock_fastmail, mock_admin):
    # Setup mocks
    mock_mailer_instance = AsyncMock()
    mock_fastmail.return_value = mock_mailer_instance
    
    otp = "123456"
    magic_token = "magic-token"
    mailer = OTPMailer(
        admin=mock_admin,
        otp=otp,
        magic_token=magic_token
    )
    
    result = await mailer.send()
    
    # Assertions
    assert result == {"message": "Email sent successfully!"}
    mock_mailer_instance.send_message.assert_called_once()
    
    # Verify message schema and template
    call_args, call_kwargs = mock_mailer_instance.send_message.call_args
    message = call_args[0]
    template_name = call_kwargs.get("template_name")
    
    assert message.subject == "Security Verification Code"
    assert message.recipients == [mock_admin.email]
    assert message.template_body["otp"] == otp
    assert message.template_body["user_name"] == mock_admin.username
    assert f"token={magic_token}" in message.template_body["magic_link"]
    assert template_name == "otp_email.html"
