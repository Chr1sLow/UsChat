import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django_redis import get_redis_connection
from .models import User, Message, ChatRoom

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.user.is_authenticated:
            user_id = self.user.id
            count = await self.increment_presence(user_id)
            # Send current online users to the connecting user
            online_users = await self.get_online_users()

            await self.send_presence_self(online_users)
            # Notify group if user just came online
            print(count)
            if count == 1:
                await self.send_presence()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.no_typing", "user": self.user.username})

        if self.user.is_authenticated:
            user_id = self.user.id
            count = await self.decrement_presence(user_id)
            # Notify group if user went offline
            print(count)
            if count == 0:
                await self.send_presence()
                
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json["type"] == "message":
            message = text_data_json["message"]

            # Save message to database
            await self.save_message(message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "user": self.user.username, "message": message}
            )
        elif text_data_json["type"] == "typing":
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.typing", "user": self.user.username})
        elif text_data_json["type"] == "no_typing":
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.no_typing", "user": self.user.username})

    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            content=content,
            user=self.scope["user"] if self.scope["user"].is_authenticated else None
        )
        
        room.messages.add(message)

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"type": "chat", "user": event["user"], "message": event["message"]}))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({"type": "typing", "user": event["user"]}))

    async def chat_no_typing(self, event):
        await self.send(text_data=json.dumps({"type": "no_typing", "user": event["user"]}))
        
    @database_sync_to_async
    def increment_presence(self, user_id):
        redis = get_redis_connection("default")
        key = f"presence:chat_{self.room_id}"
        print(f"Incrementing presence for user {user_id} in {key}")
        return redis.hincrby(key, user_id, 1)

    @database_sync_to_async
    def decrement_presence(self, user_id):
        redis = get_redis_connection("default")
        key = f"presence:chat_{self.room_id}"
        count = redis.hincrby(key, user_id, -1)
        redis.hdel(key, user_id)
        print(f"Decrementing presence for user {user_id} in {key}")
        if count <= 0:
            redis.hdel(key, user_id)

        return count

    @database_sync_to_async
    def get_online_users(self):
        redis = get_redis_connection("default")
        key = f"presence:chat_{self.room_id}"
        user_ids = [int(uid.decode()) for uid in redis.hkeys(key)]
        users = User.objects.filter(id__in=user_ids)

        return [{"id": user.id, "username": user.username} for user in users]
    
    async def send_presence(self):
        online_users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "presence.update", "online_users": online_users}
        )

    async def send_presence_self(self, online_users):
        await self.send(text_data=json.dumps({
            "type": "presence",
            "online_users": online_users
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "presence",
            "online_users": event["online_users"]
        }))