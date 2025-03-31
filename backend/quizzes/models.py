from django.db import models
import bcrypt
import uuid

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField(foreign_key='course_id')
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    
    