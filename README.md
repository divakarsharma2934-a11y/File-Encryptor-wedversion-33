# File Locker Django Project

This is a Django web application that integrates `locker.py` for file encryption and decryption.

## Features
- Encrypt files using XOR, Base64, or XOR+Base64.
- Decrypt files.
- Simple web interface.

## Setup

1. **Install Dependencies:**
   Ensure you have Django installed.
   ```bash
   pip install django
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Run the Server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the App:**
   Open your browser and go to `http://127.0.0.1:8000/`.

## Usage
1. Select a file to upload.
2. Enter an encryption key (required for XOR modes).
3. Select the algorithm.
4. Choose Encrypt or Decrypt.
5. Click "Process File" to download the result.
