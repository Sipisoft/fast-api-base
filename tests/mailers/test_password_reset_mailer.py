import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.mailers.password_reset_mailer import PasswordResetMailer
from fastapi import Request
from pydantic import EmailStr

class MockAccount:
    def __init__(self, email: str, name: str = "Test User"):
        self.email = email
        self.name = name

@pytest.fixture
def mock_account():
    return MockAccount(email="test@example.com")

@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.base_url = "http://localhost:8000/"
    request.url_for = MagicMock(return_value="http://localhost:8000/static/images/logo.png")
    return request

@pytest.mark.anyio
@patch("src.mailers.base_mailer.FastMail")
@patch("src.mailers.base_mailer.ConnectionConfig")
async def test_password_reset_mailer_send_success(mock_conf, mock_fastmail, mock_account, mock_request):
    # Setup mocks
    mock_mailer_instance = AsyncMock()
    mock_fastmail.return_value = mock_mailer_instance
    
    password_token = "fake-token"
    mailer = PasswordResetMailer(
        account=mock_account,
        password_token=password_token,
        new_password=False,
        request=mock_request
    )
    
    result = await mailer.send()
    
    # Assertions
    assert result == {"message": "Email sent successfully!"}
    mock_mailer_instance.send_message.assert_called_once()
    
    # Verify message schema
    call_args = mock_mailer_instance.send_message.call_args[0][0]
    assert call_args.subject == "Miverify - Reset Password for your account "
    assert call_args.recipients == [mock_account.email]
    assert call_args.subtype.value == "html"
    assert "set-password?token=fake-token&amp;new_password=False" in call_args.body

@pytest.mark.anyio
@patch("src.mailers.base_mailer.FastMail")
@patch("src.mailers.base_mailer.ConnectionConfig")
async def test_password_reset_mailer_new_password_true(mock_conf, mock_fastmail, mock_account, mock_request):
    # Setup mocks
    mock_mailer_instance = AsyncMock()
    mock_fastmail.return_value = mock_mailer_instance
    
    password_token = "new-user-token"
    mailer = PasswordResetMailer(
        account=mock_account,
        password_token=password_token,
        new_password=True,
        request=mock_request
    )
    
    await mailer.send()
    
    # Verify message schema
    call_args = mock_mailer_instance.send_message.call_args[0][0]
    assert call_args.subject == "Miverify - Set A Password for your account "
    # The rendered HTML will have the full URL with &amp; if we're not careful, 
    # but Jinja2 by default might escape & in attributes.
    # From the failure, it seems it's there.
    assert "set-password?token=new-user-token&amp;new_password=True" in call_args.body

@pytest.mark.anyio
@patch("src.mailers.base_mailer.FastMail")
@patch("src.mailers.base_mailer.ConnectionConfig")
@patch("os.getenv")
async def test_password_reset_mailer_frontend_url_env(mock_getenv, mock_conf, mock_fastmail, mock_account, mock_request):
    mock_getenv.side_effect = lambda k, d=None: "https://frontend.example.com/" if k == "FRONTEND_URL" else d
    
    mock_mailer_instance = AsyncMock()
    mock_fastmail.return_value = mock_mailer_instance
    
    mailer = PasswordResetMailer(
        account=mock_account,
        password_token="env-token",
        new_password=False,
        request=mock_request
    )
    
    await mailer.send()
    
    call_args = mock_mailer_instance.send_message.call_args[0][0]
    assert "https://frontend.example.com/set-password?token=env-token" in call_args.body
