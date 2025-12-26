import requests
import json
import time

url = "http://localhost:8866/ocr"
file_path = "test_ocr_image.png"

# Wait for server to potentially start up if run immediately
time.sleep(2)

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        print(f"Sending request to {url}...")
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Error Response: {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")
