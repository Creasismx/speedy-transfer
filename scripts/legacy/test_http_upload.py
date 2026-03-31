
import requests
import os

# Define the URL - adjust port if needed
URL = "http://127.0.0.1:8000/test_upload/"

def test_upload():
    print(f"Testing upload to {URL}...")
    
    # Create a small dummy file
    filename = "test_image.jpg"
    with open(filename, "wb") as f:
        f.write(b"fake image content" * 100)
    
    try:
        # Open the file in binary mode
        with open(filename, "rb") as f:
            files = {"image": (filename, f, "image/jpeg")}
            
            # Send POST request
            response = requests.post(URL, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Server handled the multipart upload correctly.")
        else:
            print("\n❌ FAILURE: Server rejected the upload or errored.")
            
    except Exception as e:
        print(f"\n❌ ERROR: Could not connect to server: {e}")
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_upload()
