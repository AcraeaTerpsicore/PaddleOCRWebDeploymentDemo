from paddleocr import PaddleOCR
import inspect
import numpy as np

print("Initializing PaddleOCR...")
# use_angle_cls=True might trigger model download
ocr = PaddleOCR(use_angle_cls=True, lang="ch")
print("OCR initialized.")

try:
    sig = inspect.signature(ocr.ocr)
    print(f"OCR ocr method signature: {sig}")
except Exception as e:
    print(f"Could not get signature: {e}")

dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

print("Testing ocr(img, cls=True)...")
try:
    ocr.ocr(dummy_img, cls=True)
    print("Success with cls=True")
except Exception as e:
    print(f"Failed with cls=True: {e}")

print("Testing ocr(img)...")
try:
    ocr.ocr(dummy_img)
    print("Success with cls=default")
except Exception as e:
    print(f"Failed with cls=default: {e}")
