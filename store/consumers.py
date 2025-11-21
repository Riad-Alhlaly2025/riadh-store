import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
            
            # Join user-specific notification group
            user = self.scope["user"]
            await self.channel_layer.group_add(
                f"user_{user.id}_notifications",
                self.channel_name
            )
            
            # Send a welcome message
            await self.send(text_data=json.dumps({
                'type': 'welcome',
                'message': 'Connected to notification service'
            }))

    async def disconnect(self, close_code):
        # Leave user-specific notification group
        user = self.scope["user"]
        if not user.is_anonymous:
            await self.channel_layer.group_discard(
                f"user_{user.id}_notifications",
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_as_read':
            notification_id = data.get('notification_id')
            # Handle marking notification as read
            await self.mark_notification_as_read(notification_id)
        elif message_type == 'request_unread_count':
            # Send current unread count
            await self.send_unread_count()

    async def mark_notification_as_read(self, notification_id):
        """Mark a notification as read"""
        try:
            # In a real implementation, you would update the database here
            # For now, we'll just send a confirmation back
            await self.send(text_data=json.dumps({
                'type': 'notification_marked_read',
                'notification_id': notification_id
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_unread_count(self):
        """Send the current unread notification count"""
        user = self.scope["user"]
        try:
            unread_count = await self.get_unread_count(user)
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def get_unread_count(self, user):
        """Get unread notification count for user"""
        # This would be implemented with database queries in a real app
        # For now, we'll return a mock value
        return 0

    # Handler for sending notifications
    async def send_notification(self, event):
        """Send notification to WebSocket"""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))