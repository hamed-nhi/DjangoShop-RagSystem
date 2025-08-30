# apps/ai_assistant/models.py

from django.db import models
from django.conf import settings # Import Django's settings
import uuid

class Conversation(models.Model):
    """
    Represents a single chat session between a user and the assistant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # This setting correctly and flexibly links to your 'accounts.CustomUser' model
    # by reading the AUTH_USER_MODEL value from your project's settings.py
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='conversations'
    )
    
    title = models.CharField(max_length=200, default="چت جدید")
    created_at = models.DateTimeField(auto_now_add=True)
    is_widget = models.BooleanField(default=False)  # جدید


    def __str__(self):
        # We use str(self.user) to be compatible with any user model's __str__ method.
        # In your case, this will correctly display "name + family".
        return f"Conversation with {self.user} - {self.title}"

    class Meta:
        # Order conversations by the most recent first
        ordering = ['-created_at']

class ChatMessage(models.Model):
    """
    Represents a single message within a conversation.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    class Meta:
        # Order messages by the oldest first within a conversation
        ordering = ['timestamp']