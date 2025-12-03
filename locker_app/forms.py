from django import forms

ALGO_CHOICES = [
    ('xor', 'XOR'),
    ('base64', 'Base64'),
    ('xor+base64', 'XOR + Base64'),
]

ACTION_CHOICES = [
    ('encrypt', 'Encrypt'),
    ('decrypt', 'Decrypt'),
]

class MultipleFileInput(forms.FileInput):
    """
    Custom widget to allow selecting multiple files in a single input field.
    """
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """
    Custom form field to handle multiple file uploads.
    """
    def to_python(self, data):
        """
        Convert the input data into a list of file objects.
        """
        if not data:
            return None
        if isinstance(data, list):
            return [super(MultipleFileField, self).to_python(f) for f in data]
        return super().to_python(data)

    def clean(self, data, initial=None):
        """
        Validate the input data and ensure it meets the field's requirements.
        """
        if not data and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        if not data:
            return None
        if isinstance(data, list):
            return [super(MultipleFileField, self).clean(f, initial) for f in data]
        return super().clean(data, initial)

class LockerForm(forms.Form):
    """
    Form for handling file encryption and decryption requests.
    Includes fields for file selection, folder selection, encryption key, algorithm, and action.
    """
    file = MultipleFileField(
        label='Select Files',
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True, 'id': 'id_file'}),
        required=False,
        error_messages={
            'missing': 'Please select at least one file or folder to process.',
            'empty': 'The submitted file is empty.'
        }
    )
    folder = MultipleFileField(
        label='Select Folder',
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True, 'webkitdirectory': True, 'directory': True, 'id': 'id_folder'}),
        required=False
    )
    folder_name = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'id_folder_name'}), required=False)
    key = forms.CharField(
        max_length=255, 
        label='Encryption Key', 
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your secret key', 'id': 'id_key'})
    )
    algorithm = forms.ChoiceField(
        choices=ALGO_CHOICES, 
        initial='xor',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES, 
        initial='encrypt', 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        """
        Perform cross-field validation to ensure either a file or folder is selected,
        and that a key is provided if the chosen algorithm requires it.
        """
        cleaned_data = super().clean()
        algo = cleaned_data.get("algorithm")
        key = cleaned_data.get("key")
        file = cleaned_data.get("file")
        folder = cleaned_data.get("folder")

        print(f"DEBUG: file field data: {file}")
        print(f"DEBUG: folder field data: {folder}")
        print(f"DEBUG: cleaned_data keys: {cleaned_data.keys()}")

        if not file and not folder:
            raise forms.ValidationError("Please select at least one file or folder.")

        if algo in ['xor', 'xor+base64'] and not key:
            self.add_error('key', 'Key is required for XOR encryption/decryption.')
        
        return cleaned_data

from django.contrib.auth.models import User

class UsernameChangeForm(forms.ModelForm):
    """
    Form for updating the username of the currently logged-in user.
    """
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'})
        }
