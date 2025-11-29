from django.contrib import admin
from .models import NotificationTemplate, Notification, EmailLog, SMSLog, PushNotificationLog, Subscription

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'is_active', 'created_at']
    list_filter = ['channel', 'is_active', 'created_at']
    search_fields = ['name', 'subject']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'channel', 'subject', 'priority', 'status', 'created_at']
    list_filter = ['channel', 'priority', 'status', 'created_at']
    search_fields = ['recipient__username', 'subject']
    readonly_fields = ['created_at', 'sent_at', 'read_at']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'provider', 'status', 'sent_at']
    list_filter = ['provider', 'status', 'sent_at']
    search_fields = ['recipient_email', 'subject']

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'provider', 'status', 'sent_at']
    list_filter = ['provider', 'status', 'sent_at']
    search_fields = ['recipient_phone']

@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['device_token', 'title', 'provider', 'status', 'sent_at']
    list_filter = ['provider', 'status', 'sent_at']
    search_fields = ['device_token', 'title']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'is_subscribed', 'created_at']
    list_filter = ['channel', 'is_subscribed', 'created_at']
    search_fields = ['user__username']