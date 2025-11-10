import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # other user's id is in the URL kwargs
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        if not self.scope["user"].is_authenticated:
            # reject anonymous
            await self.close()
            return

        # construct deterministic room name (small_id_big_id)
        users = sorted([str(self.scope['user'].id), str(self.other_user_id)], key=int)
        self.room_name = f"chat_{users[0]}_{users[1]}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        if not message:
            return

        sender = self.scope["user"]
        receiver = await self.get_user(self.other_user_id)

        msg_obj = await self.save_message(sender, receiver, message)

        payload = {
            "type": "chat.message",
            "sender_id": sender.id,
            "sender_username": sender.username,
            "message": msg_obj.message,
            "timestamp": msg_obj.timestamp.isoformat(),
        }

        # broadcast to room
        await self.channel_layer.group_send(self.room_name, {"type": "chat.message", "payload": payload})

    async def chat_message(self, event):
        # channel layer delivers here
        payload = event.get("payload")
        await self.send(text_data=json.dumps(payload))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        return ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
