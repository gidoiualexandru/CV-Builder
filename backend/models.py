from django.db import models
from django.contrib.auth.models import User

class BaseTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='base_templates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class GeneratedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_template = models.ForeignKey(BaseTemplate, on_delete=models.CASCADE)
    job_description = models.TextField()
    generated_file = models.FileField(upload_to='generated_resumes/')
    created_at = models.DateTimeField(auto_now_add=True)