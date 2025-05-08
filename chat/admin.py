from django.contrib import admin

# Register your models here.
from .models import User, ChatRoom, Message

admin.site.register(User)
admin.site.register(ChatRoom)
admin.site.register(Message)