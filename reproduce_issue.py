
import os
import sys
import django

# Setup Django environment to import locker
sys.path.append('c:/Users/divak_nikjjc1/OneDrive/Desktop/ojtproject/ojt/file_locker_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_locker_project.settings')
django.setup()

from locker_app import locker

def test_encryption():
    data = b"Hello World"
    key = b"secret"
    
    print("Testing XOR...")
    encrypted = locker.encrypt_data(data, key, "xor")
    decrypted = locker.decrypt_data(encrypted, key, "xor")
    if data == decrypted:
        print("XOR Success")
    else:
        print(f"XOR Failed: {decrypted}")

    print("\nTesting Base64...")
    encrypted = locker.encrypt_data(data, key, "base64")
    decrypted = locker.decrypt_data(encrypted, key, "base64")
    if data == decrypted:
        print("Base64 Success")
    else:
        print(f"Base64 Failed: {decrypted}")

    print("\nTesting XOR+Base64...")
    encrypted = locker.encrypt_data(data, key, "xor+base64")
    decrypted = locker.decrypt_data(encrypted, key, "xor+base64")
    if data == decrypted:
        print("XOR+Base64 Success")
    else:
        print(f"XOR+Base64 Failed: {decrypted}")

if __name__ == "__main__":
    test_encryption()
