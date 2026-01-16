from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from . import forms
from .forms import LockerForm
from .models import FileHistory
from . import locker
import zipfile
import tempfile
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User

@csrf_exempt
def google_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_token = data.get('id_token')
            
            # Verify token with Firebase Identity Toolkit
            # This is required because Firebase ID tokens are not checking against standard Google OAuth2 endpoints
            api_key = "AIzaSyAd_a-I9U014ArpshXVAaSDL8hRHG4a4_k"
            verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
            
            response = requests.post(verify_url, json={'idToken': id_token})
            
            if response.status_code != 200:
                print(f"Token verification failed: {response.text}") # Debug
                error_detail = response.json().get('error', {}).get('message', response.text)
                return JsonResponse({'success': False, 'error': f"Firebase rejected token: {error_detail}"})
                
            firebase_data = response.json()
            users = firebase_data.get('users', [])
            if not users:
                 return JsonResponse({'success': False, 'error': 'No user found in token'})
            
            email = users[0].get('email')
            
            if not email:
                 return JsonResponse({'success': False, 'error': 'No email found'})
            
            # Get or create user
            is_new_user = False
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user
                is_new_user = True
                username = email.split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                    
                user = User.objects.create_user(username=username, email=email)
                user.save()
            
            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return JsonResponse({'success': True, 'is_new_user': is_new_user})
            
        except Exception as e:
            print(f"Login exception: {str(e)}") # Debug
            return JsonResponse({'success': False, 'error': str(e)})
            
    # If GET request or other method, redirect to login
    return redirect('login')

def signup(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    """
    Display the user's profile and file operation history.
    """
    history = FileHistory.objects.filter(user=request.user)[:20]
    return render(request, 'locker_app/profile.html', {'history': history})

def home(request):
    """
    Handle the home page view, including file upload, encryption, and decryption.
    """
    if request.method == 'POST':
        print(f"FILES received: {request.FILES.keys()}") # Debugging
        form = LockerForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('file') + request.FILES.getlist('folder')
            key = form.cleaned_data['key']
            algo = form.cleaned_data['algorithm']
            action = form.cleaned_data['action']
            
            key_bytes = key.encode('utf-8') if key else b''
            
            try:
                if action == 'encrypt':
                    # Create a ZIP file using a temporary file to save memory
                    # SpooledTemporaryFile will keep data in memory until it exceeds max_size (e.g., 10MB), then spill to disk
                    # We use a regular TemporaryFile here because SpooledTemporaryFile might be tricky with streaming if it rolls over?
                    # Actually Spooled is fine, but we need to manage the lifecycle.
                    # We'll use a generator to close it.
                    
                    tmp_file = tempfile.SpooledTemporaryFile(max_size=10*1024*1024, mode='w+b')
                    with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_STORED) as zip_file:
                        for f in uploaded_files:
                            if f.multiple_chunks():
                                with zip_file.open(f.name, 'w') as dest:
                                    for chunk in f.chunks():
                                        dest.write(chunk)
                            else:
                                zip_file.writestr(f.name, f.read())
                    
                    # Reset file pointer
                    tmp_file.seek(0)
                    
                    # Generator to stream response and close file
                    def stream_response(file_obj, key, algo):
                        try:
                            yield from locker.encrypt_stream(file_obj, key, algo)
                        finally:
                            file_obj.close()

                    filename = "locked_files.zip.enc"
                    
                    # Save history (approximate size or just log it)
                    if request.user.is_authenticated:
                        folder_name = form.cleaned_data.get('folder_name')
                        if folder_name:
                            filename_display = f"Folder: {folder_name} ({len(uploaded_files)} files)"
                        elif len(uploaded_files) > 1:
                            filename_display = f"Batch Upload ({len(uploaded_files)} files)"
                        else:
                            filename_display = uploaded_files[0].name

                        FileHistory.objects.create(
                            user=request.user,
                            action=action,
                            filename=filename_display[:255]
                        )

                    response = StreamingHttpResponse(
                        stream_response(tmp_file, key_bytes, algo),
                        content_type='application/octet-stream'
                    )
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                    
                else:
                    # Decrypt
                    # We assume the user uploads the single encrypted file
                    # If they upload multiple, we only process the first one for safety/simplicity
                    if len(uploaded_files) > 1:
                        messages.warning(request, "Multiple files selected for decryption. Only the first one was processed.")
                    
                    uploaded_file = uploaded_files[0]
                    file_data = uploaded_file.read()
                    
                    result = locker.decrypt_data(file_data, key_bytes, algo)
                    # The result should be a zip file if it was encrypted by us
                    filename = "unlocked_files.zip"
                
                # Save to history only if user is authenticated (Moved up for encryption, keep here for decryption)
                if request.user.is_authenticated and action == 'decrypt':
                    FileHistory.objects.create(
                        user=request.user,
                        action=action,
                        filename=uploaded_files[0].name[:255]
                    )
                
                response = HttpResponse(result, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            except ValueError as e:
                messages.error(request, f"Decryption failed: {str(e)}")
            except Exception as e:
                messages.error(request, f"Processing failed: {str(e)}")
        else:
            # DEBUG: Add error to see what was received
            form.add_error(None, f"DEBUG: Files received: {list(request.FILES.keys())}")
    else:
        form = LockerForm()

    return render(request, 'locker_app/home.html', {'form': form})

@login_required
def change_username(request):
    """
    Handle username change requests.
    """
    if request.method == 'POST':
        form = forms.UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username updated successfully!')
            return redirect('profile')
    else:
        form = forms.UsernameChangeForm(instance=request.user)
    return render(request, 'locker_app/change_username.html', {'form': form})

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class CustomPasswordChangeView(PasswordChangeView):
    """
    View for handling user password changes.
    """
    template_name = 'locker_app/change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        """
        Handle valid form submission for password change.
        """
        messages.success(self.request, 'Password updated successfully!')
        return super().form_valid(form)
