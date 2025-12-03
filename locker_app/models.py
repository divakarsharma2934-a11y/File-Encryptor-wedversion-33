from django.db import models
from django.contrib.auth.models import User

class FileHistory(models.Model):
    """
    Model to store the history of file operations (encryption/decryption) performed by users.
    """
    ACTION_CHOICES = [
        ('encrypt', 'Encrypt'),
        ('decrypt', 'Decrypt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    filename = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return a string representation of the file history entry.
        """
        return f"{self.user.username} - {self.action} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
