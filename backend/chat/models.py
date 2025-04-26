from django.db import models

# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

# User = get_user_model()


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Message(models.Model):
    SENDER_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.content[:30]}..."
