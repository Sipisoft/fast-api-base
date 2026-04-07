import os
import cv2
import numpy as np
import pytest
from src.utils.images import adjust_brightness, optimize_image_brightness, encode_image_to_base64

def test_adjust_brightness():
    # Create a dark image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image.fill(50)  # Dark gray
    
    adjusted = adjust_brightness(image, target_brightness=150.0)
    
    # Check if mean brightness increased
    assert np.mean(cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)) > 50
    assert adjusted.shape == image.shape

def test_optimize_image_brightness(tmp_path):
    # Create a test image
    image_path = str(tmp_path / "test.jpg")
    image = np.zeros((1000, 1000, 3), dtype=np.uint8)
    image.fill(100)
    cv2.imwrite(image_path, image)
    
    output_path = optimize_image_brightness(image_path)
    
    assert os.path.exists(output_path)
    assert "_optimized.jpg" in output_path
    
    # Check if resized (optimize_image_brightness resizes to max 500)
    optimized_image = cv2.imread(output_path)
    h, w = optimized_image.shape[:2]
    assert h <= 500
    assert w <= 500

def test_encode_image_to_base64(tmp_path):
    image_path = str(tmp_path / "test.txt")
    with open(image_path, "wb") as f:
        f.write(b"fake data")
    
    encoded = encode_image_to_base64(image_path)
    assert isinstance(encoded, str)
    assert len(encoded) > 0
    
def test_optimize_image_brightness_invalid_path():
    with pytest.raises(ValueError, match="Could not load image from"):
        optimize_image_brightness("non_existent.jpg")
