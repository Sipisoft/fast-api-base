import pytest
from unittest.mock import MagicMock, patch
from src.workers.send_email import trigger_password_reset_email
from uuid import uuid4

@patch("src.workers.send_email.send_password_reset_email_task")
def test_trigger_password_reset_email(mock_task):
    # Setup
    admin_id = uuid4()
    admin = MagicMock()
    admin.id = admin_id
    
    # Execute
    trigger_password_reset_email(admin, "admin", True)
    
    # Assert
    mock_task.delay.assert_called_once_with(str(admin_id), "admin", True)
