import os
from unittest.mock import MagicMock
from src.utils.files import save_image_locally, UPLOAD_DIR

def test_save_image_locally(tmp_path):
    # Mock UploadFile
    mock_file = MagicMock()
    mock_file.filename = "test_image.jpg"
    mock_file.file.read.return_value = b"fake image content"
    
    # We need to monkeypatch UPLOAD_DIR because it's a constant in the module
    import src.utils.files
    original_upload_dir = src.utils.files.UPLOAD_DIR
    temp_upload_dir = str(tmp_path / "uploads")
    src.utils.files.UPLOAD_DIR = temp_upload_dir
    
    try:
        file_path = save_image_locally(mock_file)
        
        assert os.path.exists(file_path)
        assert file_path.startswith(temp_upload_dir)
        assert file_path.endswith(".jpg")
        
        with open(file_path, "rb") as f:
            assert f.read() == b"fake image content"
    finally:
        src.utils.files.UPLOAD_DIR = original_upload_dir
