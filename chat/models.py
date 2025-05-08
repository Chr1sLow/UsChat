from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    friends = models.ManyToManyField("User", blank=True, related_name="mutuals")
    sent_friend_requests = models.ManyToManyField("User", blank=True, related_name="sent_request")
    recieved_friend_requests = models.ManyToManyField("User", blank=True, related_name="recieved_request")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "friends": [friend.username for friend in self.friends.all()]
        }


class ChatRoom(models.Model):
    name = models.CharField(max_length=225)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="owner")
    members = models.ManyToManyField("User", blank=True, related_name="members")
    messages = models.ManyToManyField("Message", blank=True, related_name="messages")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner.id,
            "members": [member.id for member in self.members.all()],
            "messages": [{"user": message.user.username if message.user else "System", "content": message.content} for message in self.messages.all()]
        }


class Message(models.Model):
    room = models.ForeignKey("ChatRoom", on_delete=models.CASCADE, related_name="message")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True, related_name="messages")

    class Meta:
        ordering = ['timestamp']