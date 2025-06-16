from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('gate', 'Gate'),
        ('surveyor', 'Surveyor'),
        ('estimator', 'Estimator'),
        ('qc', 'Quality Control'),
        ('cs', 'Customer Service'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cs')

    def __str__(self):
        return f"{self.username} ({self.role})"
