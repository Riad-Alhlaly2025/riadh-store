"""
Social Media Service Module
Provides real API connections to various social media platforms
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from store.models import SocialMediaIntegration, Product

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Service class for handling social media API integrations"""
    
    def __init__(self):
        # API credentials would typically be stored in Django settings
        self.facebook_access_token = getattr(settings, 'FACEBOOK_ACCESS_TOKEN', None)
        self.twitter_bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', None)
        self.instagram_access_token = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', None)
        self.linkedin_access_token = getattr(settings, 'LINKEDIN_ACCESS_TOKEN', None)
        
    def post_to_facebook(self, integration: SocialMediaIntegration, message: str) -> Dict[str, Any]:
        """
        Post content to Facebook
        
        Args:
            integration: SocialMediaIntegration instance
            message: Content to post
            
        Returns:
            Dictionary with success status and response data
        """
        if not self.facebook_access_token:
            return {
                'success': False,
                'error': 'Facebook access token not configured'
            }
            
        try:
            # For products, we might want to include image
            url = f"https://graph.facebook.com/v18.0/me/feed"
            payload = {
                'message': message,
                'access_token': self.facebook_access_token
            }
            
            # If product has image, we would upload it first
            if integration.product.image:
                # This would be a more complex implementation with photo upload
                pass
                
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'post_id': data.get('id'),
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'Facebook API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_to_twitter(self, integration: SocialMediaIntegration, message: str) -> Dict[str, Any]:
        """
        Post content to Twitter
        
        Args:
            integration: SocialMediaIntegration instance
            message: Content to post (max 280 characters)
            
        Returns:
            Dictionary with success status and response data
        """
        if not self.twitter_bearer_token:
            return {
                'success': False,
                'error': 'Twitter bearer token not configured'
            }
            
        try:
            # Ensure message is within Twitter's character limit
            if len(message) > 280:
                message = message[:277] + "..."
                
            url = "https://api.twitter.com/2/tweets"
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'text': message
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'post_id': data.get('data', {}).get('id'),
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'Twitter API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_to_instagram(self, integration: SocialMediaIntegration, message: str) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            integration: SocialMediaIntegration instance
            message: Caption for the post
            
        Returns:
            Dictionary with success status and response data
        """
        if not self.instagram_access_token:
            return {
                'success': False,
                'error': 'Instagram access token not configured'
            }
            
        try:
            # Instagram requires container creation first
            # This is a simplified version - full implementation would be more complex
            url = f"https://graph.instagram.com/v18.0/me/media"
            payload = {
                'caption': message,
                'access_token': self.instagram_access_token
            }
            
            # If product has image, we would include it
            if integration.product.image:
                # Add image URL to payload
                # This is a placeholder - real implementation would upload the image
                payload['image_url'] = integration.product.image.url
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'media_id': data.get('id'),
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'Instagram API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error posting to Instagram: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_to_linkedin(self, integration: SocialMediaIntegration, message: str) -> Dict[str, Any]:
        """
        Post content to LinkedIn
        
        Args:
            integration: SocialMediaIntegration instance
            message: Content to post
            
        Returns:
            Dictionary with success status and response data
        """
        if not self.linkedin_access_token:
            return {
                'success': False,
                'error': 'LinkedIn access token not configured'
            }
            
        try:
            # Get user's organization ID first
            user_url = "https://api.linkedin.com/v2/userinfo"
            headers = {
                'Authorization': f'Bearer {self.linkedin_access_token}'
            }
            
            user_response = requests.get(user_url, headers=headers, timeout=30)
            
            if user_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'LinkedIn user info error: {user_response.text}'
                }
            
            user_data = user_response.json()
            user_id = user_data.get('sub')
            
            # Post content
            url = "https://api.linkedin.com/v2/ugcPosts"
            payload = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'post_id': data.get('id'),
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'LinkedIn API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_product_post_content(self, product: Product) -> str:
        """
        Generate social media post content for a product
        
        Args:
            product: Product instance
            
        Returns:
            Formatted post content
        """
        # Generate content based on product information
        content = f"🔥 جديد في المتجر! 🔥\n\n"
        content += f"منتج: {product.name}\n"
        content += f"السعر: {product.price} {product.get_currency_display()}\n"
        
        if product.description:
            # Limit description length for social media
            desc = product.description[:100] + "..." if len(product.description) > 100 else product.description
            content += f"الوصف: {desc}\n\n"
            
        content += "#متجر_إلكتروني #عروض_جديدة #تسوق_آنلاين"
        
        return content
    
    def post_product_to_platform(self, integration: SocialMediaIntegration) -> Dict[str, Any]:
        """
        Post a product to a specific social media platform
        
        Args:
            integration: SocialMediaIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        # Generate content for the product
        content = self.generate_product_post_content(integration.product)
        
        # Post to the appropriate platform
        if integration.platform == 'facebook':
            return self.post_to_facebook(integration, content)
        elif integration.platform == 'twitter':
            return self.post_to_twitter(integration, content)
        elif integration.platform == 'instagram':
            return self.post_to_instagram(integration, content)
        elif integration.platform == 'linkedin':
            return self.post_to_linkedin(integration, content)
        else:
            return {
                'success': False,
                'error': f'Unsupported platform: {integration.platform}'
            }

# Singleton instance for easy access
social_media_service = SocialMediaService()