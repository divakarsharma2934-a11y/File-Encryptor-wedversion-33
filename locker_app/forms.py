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
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def to_python(self, data):
        if not data:
            return None
        if isinstance(data, list):
            return [super(MultipleFileField, self).to_python(f) for f in data]
        return super().to_python(data)

    def clean(self, data, initial=None):
        if not data and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        if not data:
            return None
        if isinstance(data, list):
            return [super(MultipleFileField, self).clean(f, initial) for f in data]
        return super().clean(data, initial)

class LockerForm(forms.Form):
    file = MultipleFileField(
        label='Select Files',
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}),
        error_messages={
            'required': 'Please select at least one file to process.',
            'missing': 'Please select at least one file to process.',
            'empty': 'The submitted file is empty.'
        }
    )
    key = forms.CharField(
        max_length=255, 
        label='Encryption Key', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your secret key'})
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
        cleaned_data = super().clean()
        algo = cleaned_data.get("algorithm")
        key = cleaned_data.get("key")

        if algo in ['xor', 'xor+base64'] and not key:
            self.add_error('key', 'Key is required for XOR encryption/decryption.')
        
        return cleaned_data
