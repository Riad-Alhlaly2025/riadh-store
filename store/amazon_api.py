import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import json
from django.conf import settings
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

class AmazonProductAPI:
    def __init__(self):
        self.access_key = getattr(settings, 'AMAZON_ACCESS_KEY', '')
        self.secret_key = getattr(settings, 'AMAZON_SECRET_KEY', '')
        self.associate_tag = getattr(settings, 'AMAZON_ASSOCIATE_TAG', '')
        self.region = 'us-east-1'
        self.service = 'ProductAdvertisingAPI'
        self.host = 'webservices.amazon.com'
        self.endpoint = f'https://{self.host}/paapi5/searchitems'
        
    def search_products(self, keywords, search_index='All', item_count=10):
        """Search for products on Amazon"""
        try:
            # Prepare request parameters
            params = {
                'Keywords': keywords,
                'SearchIndex': search_index,
                'ItemCount': item_count,
                'PartnerTag': self.associate_tag,
                'PartnerType': 'Associates',
                'Marketplace': 'www.amazon.com'
            }
            
            # Make request to Amazon API
            response = self._make_request('SearchItems', params)
            return self._parse_search_response(response)
        except Exception as e:
            print(f"Error searching Amazon products: {str(e)}")
            return []
    
    def get_product_details(self, asin):
        """Get detailed information for a specific product"""
        try:
            # Prepare request parameters
            params = {
                'ASIN': asin,
                'PartnerTag': self.associate_tag,
                'PartnerType': 'Associates',
                'Marketplace': 'www.amazon.com'
            }
            
            # Make request to Amazon API
            response = self._make_request('GetItems', params)
            return self._parse_item_response(response)
        except Exception as e:
            print(f"Error getting Amazon product details: {str(e)}")
            return None
    
    def _make_request(self, operation, params):
        """Make signed request to Amazon API"""
        # This is a simplified implementation
        # In production, you would use boto3 or a proper Amazon API client
        request_params = {
            'Operation': operation,
            'Service': self.service,
            'Timestamp': self._get_timestamp(),
            'Version': '2013-08-01',
            **params
        }
        
        # Sort parameters
        sorted_params = sorted(request_params.items())
        query_string = urlencode(sorted_params)
        
        # Create signature (simplified)
        # In production, use proper AWS signature v4
        url = f"https://{self.host}/onca/xml?{query_string}"
        return requests.get(url)
    
    def _parse_search_response(self, response):
        """Parse Amazon search response"""
        try:
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract product information
            products = []
            items = root.find('.//Items')
            if items is not None:
                for item in items.findall('.//Item'):
                    product = {
                        'asin': item.findtext('ASIN', ''),
                        'title': item.findtext('ItemAttributes/Title', ''),
                        'price': item.findtext('OfferSummary/LowestNewPrice/Amount', '0'),
                        'currency': item.findtext('OfferSummary/LowestNewPrice/CurrencyCode', 'USD'),
                        'image_url': item.findtext('LargeImage/URL', ''),
                        'detail_page_url': item.findtext('DetailPageURL', ''),
                    }
                    products.append(product)
            
            return products
        except Exception as e:
            print(f"Error parsing Amazon response: {str(e)}")
            return []
    
    def _parse_item_response(self, response):
        """Parse Amazon item detail response"""
        try:
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract product information
            item = root.find('.//Item')
            if item is not None:
                product = {
                    'asin': item.findtext('ASIN', ''),
                    'title': item.findtext('ItemAttributes/Title', ''),
                    'description': item.findtext('EditorialReviews/EditorialReview/Content', ''),
                    'price': item.findtext('OfferSummary/LowestNewPrice/Amount', '0'),
                    'currency': item.findtext('OfferSummary/LowestNewPrice/CurrencyCode', 'USD'),
                    'image_url': item.findtext('LargeImage/URL', ''),
                    'detail_page_url': item.findtext('DetailPageURL', ''),
                    'brand': item.findtext('ItemAttributes/Brand', ''),
                    'manufacturer': item.findtext('ItemAttributes/Manufacturer', ''),
                }
                return product
            
            return None
        except Exception as e:
            print(f"Error parsing Amazon item response: {str(e)}")
            return None
    
    def _get_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Usage example:
# amazon_api = AmazonProductAPI()
# products = amazon_api.search_products("laptop", "Electronics", 10)