import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads/images"

def save_image_locally(file: UploadFile) -> str:
    print("FILE", file)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        contents = file.file.read()
        f.write(contents)

    return file_path  