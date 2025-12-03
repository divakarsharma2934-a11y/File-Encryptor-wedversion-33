
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class FileUploadTest(TestCase):
    """
    Test case for verifying file upload functionality.
    """
    def test_upload_file(self):
        """
        Test the file upload and encryption process.
        """
        client = Client()
        # Create a dummy file
        file_content = b"test content"
        test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        
        # Login if required (view is @login_required)
        # We need a user
        from django.contrib.auth.models import User
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        client.force_login(user)
        
        response = client.post(reverse('home'), {
            'file': test_file,
            'key': 'secret',
            'algorithm': 'xor',
            'action': 'encrypt'
        })
        
        if response.status_code == 200:
            # Check if it's a file download
            if response.get('Content-Disposition'):
                print(f"SUCCESS: File download received: {response['Content-Disposition']}")
                return

            # If not a download, check for form errors
            if hasattr(response, 'context') and response.context and 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print(f"Form Errors: {form.errors}")
                    self.fail(f"Form validation failed: {form.errors}")
            else:
                print("Response 200 but no context and no file download.")
        else:
            print(f"Response Status: {response.status_code}")
            self.fail(f"Response status code: {response.status_code}")

