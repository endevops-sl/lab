from django.db import models
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os

class Client(models.Model):
    # API properties
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=255)
    given_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    email = models.EmailField()
    company_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    invite_url = models.URLField(null=True, blank=True)
    avatar_image_url = models.URLField(null=True, blank=True)
    first_login_date = models.DateTimeField(null=True, blank=True)
    last_login_date = models.DateTimeField(null=True, blank=True)
    creation_method = models.CharField(max_length=255)
    custom_fields = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.given_name} {self.family_name}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
        ('Cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    shared_on = models.DateTimeField(auto_now_add=True)
    send_email = models.BooleanField(default=False, verbose_name='Send Email')
    file = models.FileField(upload_to='invoices/')

    def __str__(self):
        return f"{self.name} - {self.status}"

    def save(self, *args, **kwargs):
        # Before saving, we capture whether the email should be sent
        # to avoid sending duplicate emails (e.g., on each .save() call)
        send_invoice_email = self.pk is None and self.send_email
        
        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Send the email after the object is created
        if send_invoice_email:
            html_content = render_to_string(
                'pixelplan/email.html',  # Path to your template
                {
                    'client_name': f"{self.client.given_name} {self.client.family_name}",
                    'invoice_name': self.name,
                    # Any other context variables you want to send to the template
                }
            )
            text_content = strip_tags(html_content)  # Create a text-only version of the email

            email = EmailMultiAlternatives(
                subject=f"Invoice {self.name}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.client.email]
            )
            email.attach_alternative(html_content, "text/html")

            if self.file and os.path.isfile(self.file.path):
                email.attach_file(self.file.path)
            
            email.send()

    class Meta:
        ordering = ['shared_on']