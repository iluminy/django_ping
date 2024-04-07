from channels.generic.websocket import AsyncWebsocketConsumer

from main.classes.connected_users import ConnectedUsers
from main.serializers import IPSerializer


connected_users = ConnectedUsers(async_mode=True)


class ListenToProcessResultsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['ip']
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        serializer = IPSerializer(data={'ip': self.group_name})
        if not serializer.is_valid():
            await self.send(text_data='IP address is not valid.\n')
            return await self.close()

        await connected_users.aadd(self.scope['user'].username, self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await connected_users.aremove(self.scope['user'].username, self.group_name)

    async def send_data(self, event):
        # Send data through WebSocket
        await self.send(text_data=event['message'])
