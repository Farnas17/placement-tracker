from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    CATEGORY_CHOICES = [
        ('DSA', 'DSA'),
        ('CORE', 'Core Subjects'),
        ('APTITUDE', 'Aptitude'),
        ('PROJECT', 'Project'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=255)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    date_assigned = models.DateField(auto_now_add=True)
    date_completed = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.category})"