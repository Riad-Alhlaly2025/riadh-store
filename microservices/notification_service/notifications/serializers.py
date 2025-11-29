from rest_framework import serializers
from .models import NotificationTemplate, Notification, Subscription

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'channel', 'subject', 'body', 'is_active', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'template', 'recipient', 'recipient_username', 'channel', 'subject', 
                  'message', 'priority', 'priority_display', 'status', 'status_display', 
                  'sent_at', 'read_at', 'metadata', 'created_at']
        read_only_fields = ['created_at', 'sent_at', 'read_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_username', 'channel', 'channel_display', 'is_subscribed', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']