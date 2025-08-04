import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Canal, CanalMensaje
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.canal_id = self.scope['url_route']['kwargs']['canal_id']
        self.room_group_name = f'chat_{self.canal_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibe mensajes del WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        mensaje = data['mensaje']
        username = self.scope["user"].username

        # Guardar el mensaje
        canal = await self.get_canal()
        user = self.scope["user"]
        await self.guardar_mensaje(canal, user, mensaje)

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'mensaje': mensaje,
                'username': username,
            }
        )

    # Enviar mensaje al WebSocket
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'mensaje': event['mensaje'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def get_canal(self):
        return Canal.objects.get(id=self.canal_id)

    @database_sync_to_async
    def guardar_mensaje(self, canal, usuario, texto):
        CanalMensaje.objects.create(canal=canal, usuario=usuario, texto=texto)
        return CanalMensaje