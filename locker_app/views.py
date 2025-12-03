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
                    with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
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
                        file_names = ', '.join([f.name for f in uploaded_files])
                        FileHistory.objects.create(
                            user=request.user,
                            action=action,
                            filename=file_names[:255]
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
