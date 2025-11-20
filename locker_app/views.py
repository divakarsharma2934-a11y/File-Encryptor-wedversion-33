from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import LockerForm
from .models import FileHistory
from . import locker
import io
import zipfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def signup(request):
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
    history = FileHistory.objects.filter(user=request.user)[:20]
    return render(request, 'locker_app/profile.html', {'history': history})

def home(request):
    if request.method == 'POST':
        print(f"FILES received: {request.FILES.keys()}") # Debugging
        form = LockerForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = request.FILES.getlist('file')
            key = form.cleaned_data['key']
            algo = form.cleaned_data['algorithm']
            action = form.cleaned_data['action']
            
            key_bytes = key.encode('utf-8') if key else b''
            
            try:
                if action == 'encrypt':
                    # Create a ZIP file in memory containing all uploaded files
                    buffer = io.BytesIO()
                    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for f in uploaded_files:
                            zip_file.writestr(f.name, f.read())
                    
                    # Get the ZIP data
                    file_data = buffer.getvalue()
                    
                    # Encrypt the ZIP data
                    result = locker.encrypt_data(file_data, key_bytes, algo)
                    filename = "locked_files.zip.enc"
                    
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
                
                # Save to history
                file_names = ', '.join([f.name for f in uploaded_files]) if action == 'encrypt' else uploaded_files[0].name
                FileHistory.objects.create(
                    user=request.user,
                    action=action,
                    filename=file_names[:255]  # Truncate if too long
                )
                
                response = HttpResponse(result, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            except Exception as e:
                messages.error(request, f"Processing failed: {str(e)}")
    else:
        form = LockerForm()

    return render(request, 'locker_app/home.html', {'form': form})
