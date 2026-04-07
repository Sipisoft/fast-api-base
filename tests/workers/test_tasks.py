import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.workers.tasks import send_otp_email_task, send_password_reset_email_task, AccountType
from src.models.admin import Admin
from uuid import uuid4

@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.OTPMailer")
def test_send_otp_email_task_success(mock_mailer_class, mock_session_local, db_session):
    # Setup
    admin_id = uuid4()
    admin = Admin(id=admin_id, email="admin@example.com", username="adminuser")
    
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = admin
    
    mock_mailer_instance = MagicMock()
    mock_mailer_instance.send = AsyncMock()
    mock_mailer_class.return_value = mock_mailer_instance
    
    # Execute
    send_otp_email_task(admin_id, "123456", "magic-token")
    
    # Assert
    mock_db.query.assert_called()
    mock_mailer_class.assert_called_once_with(admin, "123456", "magic-token")
    mock_mailer_instance.send.assert_called_once()
    mock_db.close.assert_called_once()

@patch("src.workers.tasks.SessionLocal")
def test_send_otp_email_task_admin_not_found(mock_session_local):
    # Setup
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    send_otp_email_task(uuid4(), "123456", "magic-token")
    
    # Assert
    mock_db.close.assert_called_once()

@patch("src.workers.tasks.SessionLocal")
@patch("src.workers.tasks.PasswordResetMailer")
def test_send_password_reset_email_task_success(mock_mailer_class, mock_session_local):
    # Setup
    admin_id = str(uuid4())
    admin = Admin(id=admin_id, email="admin@example.com", password_reset_token="token123")
    
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = admin
    
    mock_mailer_instance = MagicMock()
    mock_mailer_instance.send = AsyncMock()
    mock_mailer_class.return_value = mock_mailer_instance
    
    # Execute
    send_password_reset_email_task(admin_id, AccountType.admin, True)
    
    # Assert
    mock_db.query.assert_called()
    mock_mailer_class.assert_called_once_with(admin, "token123", True)
    mock_mailer_instance.send.assert_called_once()
    mock_db.close.assert_called_once()

def test_send_password_reset_email_task_user_type():
    # Current implementation returns immediately if account_type is user
    # but it still opens the DB session because it's in the try block's parent scope?
    # Wait, let's check the code again.
    with patch("src.workers.tasks.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        send_password_reset_email_task("some-id", AccountType.user, True)
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
