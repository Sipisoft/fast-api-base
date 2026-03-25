import base64

import os
import cv2
from src.models.admin import Admin
import numpy as np

CONTENT_TYPES = {
    "image/jpeg": "JPG",
    "image/jpg": "JPG",
    "image/png": "PNG"
}

def adjust_brightness(image: np.ndarray, target_brightness: float = 140.0) -> np.ndarray:
  
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_brightness = np.mean(gray)
    print(f"Current brightness: {current_brightness:.2f}")

  
    scale = target_brightness / (current_brightness + 1e-5)
    scale = np.clip(scale, 0.5, 2.0)  # prevent over/under-exposure

  
    adjusted = cv2.convertScaleAbs(image, alpha=scale, beta=0)
    return adjusted

def optimize_image_brightness(input_path: str):
  
    image = cv2.imread(input_path)
    



    if image is None:
        raise ValueError(f"Could not load image from {input_path}")
    
    output_path = input_path.replace(".jpg", "_optimized.jpg")
    height, width = image.shape[:2]

    # Target max width and height
    max_dim = 500

    # Calculate scaling factor to fit within 500x500
    scaling_factor = min(max_dim / width, max_dim / height)
    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    # Resize the image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    
    
    optimized = adjust_brightness(resized)
    
    cv2.imwrite(output_path, optimized)
    return output_path
    
def encode_image_to_base64(path: str) -> str:
    with open(path, "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read())
        encoded_str = encoded_bytes.decode("utf-8")
        return encoded_str




