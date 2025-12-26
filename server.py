from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from io import BytesIO
import cv2
import numpy as np
import paddle

app = FastAPI()

# Enable CORS to allow requests from the frontend (file:// or localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PaddleOCR with angle classification and Chinese language support
# The first run will download the necessary models
# ocr = PaddleOCR(use_angle_cls=True, lang="ch")

# Check if GPU is available
gpu_available = paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0

# Re-initialize PaddleOCR with GPU support and optimizations
ocr = PaddleOCR(
    use_textline_orientation=True, 
    lang="ch",
    device="gpu" if gpu_available else "cpu",
    precision="fp16" if gpu_available else "fp32"
)

@app.post("/ocr")
async def recognize(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Convert binary content to a format CV2 can read
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Perform OCR
        # cls=True argument removed due to API mismatch in installed version
        result_raw = ocr.ocr(img)
        print(f"DEBUG: Result Type: {type(result_raw)}")
        
        # Check if result_raw is a list containing a dict with 'rec_texts' (New PaddleOCR/PaddleX format)
        final_result = []
        if isinstance(result_raw, list):
            for item in result_raw:
                # Handle dictionary response (likely from PaddleX)
                if isinstance(item, dict) and 'rec_texts' in item:
                     final_result.extend(item['rec_texts'])
                # Handle dictionary string representation (if valid dict inside string? No, handles native dict)
                # Handle old style [[box, (text, score)], ...]
                elif isinstance(item, list):
                    for line in item:
                        if isinstance(line, list) and len(line) == 2 and isinstance(line[1], tuple):
                             final_result.append(line[1][0])
        
        # If we didn't extract anything specific but have content, fall back to robust serialization
        def to_serializable(val):
            if isinstance(val, (np.integer, np.int64, np.int32)):
                return int(val)
            if isinstance(val, (np.floating, np.float32, np.float64)):
                return float(val)
            if isinstance(val, np.ndarray):
                return val.tolist()
            if isinstance(val, list):
                return [to_serializable(x) for x in val]
            if isinstance(val, tuple):
                return tuple(to_serializable(x) for x in val)
            if isinstance(val, dict):
                return {k: to_serializable(v) for k, v in val.items()}
            # Fallback: convert unknown types to string
            if hasattr(val, "tolist"):
                    return val.tolist()
            return str(val)

        if not final_result and result_raw:
             final_result = to_serializable(result_raw)
        
        return {
            "result": final_result,
            "full_data": to_serializable(result_raw)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
