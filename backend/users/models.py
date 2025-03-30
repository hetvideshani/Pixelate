import uuid
from django.db import models

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    role = models.CharField(max_length=50, choices=[('student', 'Student'), ('mentor', 'Mentor'), ('admin', 'Admin')], default='student')
    preferred_language = models.CharField(max_length=50, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
