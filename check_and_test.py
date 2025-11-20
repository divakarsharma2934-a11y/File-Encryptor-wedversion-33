
import os
import sys
import django
import io
import zipfile

# Setup Django environment
sys.path.append('c:/Users/divak_nikjjc1/OneDrive/Desktop/ojtproject/ojt/file_locker_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_locker_project.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from locker_app import locker

def check_google_app():
    print("--- Checking Google App ---")
    try:
        app = SocialApp.objects.get(provider='google')
        print(f"App found: {app.name}")
        print(f"Client ID: {app.client_id}")
        print(f"Secret: {app.secret}")
        if app.client_id == 'DUMMY_CLIENT_ID':
            print("WARNING: Using dummy credentials!")
    except SocialApp.DoesNotExist:
        print("Google App not found!")

def test_full_flow():
    print("\n--- Testing Full Encryption Flow ---")
    
    # 1. Create dummy file content
    original_filename = "test.txt"
    original_content = b"This is a secret message."
    
    # 2. Zip it (simulating views.py)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(original_filename, original_content)
    
    zip_data = buffer.getvalue()
    print(f"Zip created, size: {len(zip_data)}")
    
    # 3. Encrypt
    key = b"secret"
    algo = "xor"
    encrypted_data = locker.encrypt_data(zip_data, key, algo)
    print(f"Encrypted data size: {len(encrypted_data)}")
    
    # 4. Decrypt
    decrypted_data = locker.decrypt_data(encrypted_data, key, algo)
    print(f"Decrypted data size: {len(decrypted_data)}")
    
    if decrypted_data != zip_data:
        print("ERROR: Decrypted data does not match original zip data!")
        return

    # 5. Unzip
    try:
        buffer_out = io.BytesIO(decrypted_data)
        with zipfile.ZipFile(buffer_out, 'r') as zip_out:
            files = zip_out.namelist()
            print(f"Files in decrypted zip: {files}")
            if original_filename in files:
                content = zip_out.read(original_filename)
                if content == original_content:
                    print("SUCCESS: Content matches!")
                else:
                    print("ERROR: Content mismatch!")
            else:
                print("ERROR: Original file not found in zip!")
    except zipfile.BadZipFile:
        print("ERROR: Decrypted data is not a valid zip file!")

if __name__ == "__main__":
    check_google_app()
    test_full_flow()
