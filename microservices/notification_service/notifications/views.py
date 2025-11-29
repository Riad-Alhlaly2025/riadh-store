from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import NotificationTemplate, Notification, Subscription
from .serializers import NotificationTemplateSerializer, NotificationSerializer, SubscriptionSerializer

# Notification Template Views
class NotificationTemplateListView(generics.ListCreateAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationTemplate.objects.all()

class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationTemplate.objects.all()

# Notification Views
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """
    Mark a notification as read
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Mark all notifications as read for the current user
    """
    try:
        notifications = Notification.objects.filter(recipient=request.user, read_at__isnull=True)
        notifications.update(read_at=timezone.now())
        
        return Response({'message': f'Marked {notifications.count()} notifications as read'})
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# Subscription Views
class SubscriptionListView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_to_channel(request):
    """
    Subscribe to a notification channel
    """
    try:
        channel = request.data.get('channel')
        if not channel:
            return Response(
                {'error': 'channel is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            channel=channel,
            defaults={'is_subscribed': True}
        )
        
        if not created and not subscription.is_subscribed:
            subscription.is_subscribed = True
            subscription.save()
        
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_from_channel(request):
    """
    Unsubscribe from a notification channel
    """
    try:
        channel = request.data.get('channel')
        if not channel:
            return Response(
                {'error': 'channel is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            channel=channel,
            defaults={'is_subscribed': False}
        )
        
        if not created and subscription.is_subscribed:
            subscription.is_subscribed = False
            subscription.save()
        
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )