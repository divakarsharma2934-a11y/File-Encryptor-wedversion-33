# File Locker Project

A secure web application for encrypting and decrypting files using various algorithms. This project allows users to upload files, apply encryption (XOR, Base64, or both), and download the secured result. It also features user authentication to track file processing history.

## 🚀 Tech Stack

*   **Backend Framework:** [Django](https://www.djangoproject.com/) (Python)
*   **Database:** SQLite (Default Django setup)
*   **Frontend:** HTML5, CSS3, Django Templates
*   **Server/Deployment:** Gunicorn, Whitenoise
*   **Encryption Logic:** Custom Python implementation (`locker.py`) using `base64` and `hashlib`.
*   Deployment Setup:
    The project is deployed on Railway using Gunicorn as the WSGI server and WhiteNoise for serving static files in production.

## 📦 Modules Used

Here is a detailed list of the key modules and libraries used in this project:

*   **[Django](https://www.djangoproject.com/)**: High-level Python web framework used for the backend logic, routing, and ORM.
*   **[Gunicorn](https://gunicorn.org/)**: Python WSGI HTTP Server for UNIX, used to serve the Django application in production.
*   **[Whitenoise](https://whitenoise.readthedocs.io/)**: Radically simplified static file serving for Python web apps, allowing the app to serve its own static files.
*   **hashlib**: Standard Python library used for hashing the encryption keys (SHA-256) to ensure security.
*   **base64**: Standard Python library used for encoding and decoding binary data to ASCII characters for the Base64 encryption algorithm.
*   **argparse**: Standard Python library used for parsing command-line arguments in the `locker.py` utility.
*   **os**: Standard Python library used for interacting with the operating system, such as file path manipulations.
*   **sys**: Standard Python library used for system-specific parameters and functions.
*   **io**: Standard Python library used for working with streams (e.g., in-memory ZIP file creation).
*   **zipfile**: Standard Python library used for creating and reading ZIP archives.

## 📂 Project Structure

Here is an overview of the key files and directories in the project:

### Root Directory
*   **`manage.py`**: Django's command-line utility for administrative tasks (running the server, migrations, etc.).
*   **`requirements.txt`**: Lists the Python dependencies required to run the project.
*   **`db.sqlite3`**: The SQLite database file storing user data and file history.
*   **`Procfile`**: Configuration for deployment (e.g., on Heroku or Render).
*   **`render-build.sh`**: Build script for deployment on Render.

### `locker_app/` (Main Application)
This directory contains the core logic of the application.

*   **`views.py`**: Handles the request/response logic.
    *   `home`: Manages file upload, encryption/decryption processing, and file download.
    *   `signup`, `profile`, `change_username`: Manage user authentication and account settings.
*   **`models.py`**: Defines the database schema.
    *   `FileHistory`: Tracks user activities (encrypt/decrypt actions, filenames, timestamps).
*   **`locker.py`**: The core utility for file security.
    *   Implements `xor_encrypt`, `xor_decrypt`, `b64_encrypt`, `b64_decrypt`.
    *   Handles key hashing (SHA-256) and file signatures (`LOCKER_V1`) to ensure data integrity.
*   **`forms.py`**: Django forms for validating user input.
    *   `LockerForm`: Handles file selection, key input, and algorithm choice.
    *   `UsernameChangeForm`: For updating user profiles.
*   **`urls.py`**: Defines the URL routing for the app.
*   **`templates/locker_app/`**: Contains HTML files for the UI (`home.html`, `profile.html`, `base.html`, etc.).
*   **`static/locker_app/`**: Contains static assets like CSS files (`home.css`, `auth.css`) for styling.

### `file_locker_project/` (Project Configuration)
*   **`settings.py`**: Global settings for the Django project (database config, installed apps, middleware).
*   **`urls.py`**: The root URL configuration that includes `locker_app` URLs.
*   **`wsgi.py`**: WSGI config for web servers.

## 🔑 Key Features

1.  **File Encryption & Decryption**:
    *   **Algorithms**: XOR, Base64, and XOR+Base64.
    *   **Security**: Uses a user-provided key, hashed with SHA-256. Adds a signature to verify integrity upon decryption.
    *   **Batch Processing**: Multiple files uploaded for encryption are automatically zipped.

2.  **User Authentication**:
    *   Sign up and Login functionality.
    *   Profile page to view the history of encrypted/decrypted files.
    *   Ability to change username and password.

## 🛠️ Setup & Installation

1.  **Clone the repository** (if applicable) or navigate to the project folder.

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```
    Access the app at `http://127.0.0.1:8000/`.

## 📝 Usage

1.  **Home Page**:
    *   Select one or more files.
    *   Enter a secret key (required for XOR).
    *   Choose an algorithm (XOR, Base64, or Both).
    *   Select "Encrypt" or "Decrypt" and submit.
    *   The processed file will be downloaded automatically.

2.  **Profile**:
    *   Log in to view a history of your file operations.
