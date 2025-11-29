"""
Shipping Service Module
Provides real API connections to various shipping providers
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from store.models import ShippingIntegration, Order

logger = logging.getLogger(__name__)

class ShippingService:
    """Service class for handling shipping provider API integrations"""
    
    def __init__(self):
        # API credentials would typically be stored in Django settings
        self.fedex_key = getattr(settings, 'FEDEX_API_KEY', None)
        self.fedex_password = getattr(settings, 'FEDEX_API_PASSWORD', None)
        self.fedex_account = getattr(settings, 'FEDEX_ACCOUNT_NUMBER', None)
        self.fedex_meter = getattr(settings, 'FEDEX_METER_NUMBER', None)
        
        self.dhl_site_id = getattr(settings, 'DHL_SITE_ID', None)
        self.dhl_password = getattr(settings, 'DHL_PASSWORD', None)
        
        self.ups_access_key = getattr(settings, 'UPS_ACCESS_KEY', None)
        self.ups_username = getattr(settings, 'UPS_USERNAME', None)
        self.ups_password = getattr(settings, 'UPS_PASSWORD', None)
        
        self.aramex_account_pin = getattr(settings, 'ARAMEX_ACCOUNT_PIN', None)
        self.aramex_account_number = getattr(settings, 'ARAMEX_ACCOUNT_NUMBER', None)
        self.aramex_account_entity = getattr(settings, 'ARAMEX_ACCOUNT_ENTITY', None)
        self.aramex_account_country_code = getattr(settings, 'ARAMEX_ACCOUNT_COUNTRY_CODE', None)
    
    def create_fedex_shipment(self, integration: ShippingIntegration) -> Dict[str, Any]:
        """
        Create a shipment with FedEx
        
        Args:
            integration: ShippingIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.fedex_key, self.fedex_password, self.fedex_account, self.fedex_meter]):
            return {
                'success': False,
                'error': 'FedEx API credentials not configured'
            }
            
        try:
            # FedEx API endpoint
            url = "https://apis.fedex.com/ship/v1/shipments"
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.get_fedex_access_token()}'
            }
            
            # Request payload - simplified for demonstration
            payload = {
                "requestedShipment": {
                    "shipper": {
                        "contact": {
                            "personName": "Store Owner",
                            "phoneNumber": "1234567890"
                        },
                        "address": {
                            "streetLines": ["Store Address Line 1"],
                            "city": "Store City",
                            "stateOrProvinceCode": "SC",
                            "postalCode": "12345",
                            "countryCode": "US"
                        }
                    },
                    "recipients": [
                        {
                            "contact": {
                                "personName": "Customer Name",
                                "phoneNumber": integration.order.phone_number
                            },
                            "address": {
                                "streetLines": [integration.order.shipping_address],
                                "city": "Customer City",
                                "stateOrProvinceCode": "CC",
                                "postalCode": "54321",
                                "countryCode": "US"
                            }
                        }
                    ],
                    "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                    "serviceType": "FEDEX_GROUND",
                    "packagingType": "YOUR_PACKAGING",
                    "totalWeight": 1.0,
                    "preferredCurrency": "USD"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracking_number = data.get('output', {}).get('transactionShipments', [{}])[0].get('masterTrackingNumber')
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'FedEx API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error creating FedEx shipment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_fedex_access_token(self) -> str:
        """
        Get FedEx API access token
        
        Returns:
            Access token string
        """
        try:
            url = "https://apis.fedex.com/oauth/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.fedex_key,
                'client_secret': self.fedex_password
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token', '')
            else:
                logger.error(f"Error getting FedEx access token: {response.text}")
                return ''
                
        except Exception as e:
            logger.error(f"Error getting FedEx access token: {str(e)}")
            return ''
    
    def create_dhl_shipment(self, integration: ShippingIntegration) -> Dict[str, Any]:
        """
        Create a shipment with DHL
        
        Args:
            integration: ShippingIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.dhl_site_id, self.dhl_password]):
            return {
                'success': False,
                'error': 'DHL API credentials not configured'
            }
            
        try:
            # DHL API endpoint
            url = "https://express.dhl.com/services/shipment/v1/shipments"
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {self.encode_credentials(self.dhl_site_id, self.dhl_password)}'
            }
            
            # Request payload - simplified for demonstration
            payload = {
                "shipment": {
                    "shipper": {
                        "name": "Store Owner",
                        "address": {
                            "addressLine1": "Store Address Line 1",
                            "city": "Store City",
                            "postalCode": "12345",
                            "countryCode": "US"
                        },
                        "contact": {
                            "phoneNumber": "1234567890"
                        }
                    },
                    "receiver": {
                        "name": "Customer Name",
                        "address": {
                            "addressLine1": integration.order.shipping_address,
                            "city": "Customer City",
                            "postalCode": "54321",
                            "countryCode": "US"
                        },
                        "contact": {
                            "phoneNumber": integration.order.phone_number
                        }
                    },
                    "packages": [
                        {
                            "weight": 1.0,
                            "dimensions": {
                                "length": 10.0,
                                "width": 8.0,
                                "height": 6.0
                            }
                        }
                    ],
                    "serviceType": "U",
                    "currency": "USD"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracking_number = data.get('shipmentTrackingNumber')
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'DHL API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error creating DHL shipment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def encode_credentials(self, site_id: str, password: str) -> str:
        """
        Encode credentials for basic authentication
        
        Args:
            site_id: DHL site ID
            password: DHL password
            
        Returns:
            Base64 encoded credentials
        """
        import base64
        credentials = f"{site_id}:{password}"
        return base64.b64encode(credentials.encode()).decode()
    
    def create_ups_shipment(self, integration: ShippingIntegration) -> Dict[str, Any]:
        """
        Create a shipment with UPS
        
        Args:
            integration: ShippingIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.ups_access_key, self.ups_username, self.ups_password]):
            return {
                'success': False,
                'error': 'UPS API credentials not configured'
            }
            
        try:
            # UPS API endpoint
            url = "https://onlinetools.ups.com/ship/v1/shipments"
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.get_ups_access_token()}',
                'AccessLicenseNumber': self.ups_access_key
            }
            
            # Request payload - simplified for demonstration
            payload = {
                "ShipmentRequest": {
                    "Shipment": {
                        "Shipper": {
                            "Name": "Store Owner",
                            "Address": {
                                "AddressLine": ["Store Address Line 1"],
                                "City": "Store City",
                                "StateProvinceCode": "SC",
                                "PostalCode": "12345",
                                "CountryCode": "US"
                            },
                            "Phone": {
                                "Number": "1234567890"
                            }
                        },
                        "ShipTo": {
                            "Name": "Customer Name",
                            "Address": {
                                "AddressLine": [integration.order.shipping_address],
                                "City": "Customer City",
                                "StateProvinceCode": "CC",
                                "PostalCode": "54321",
                                "CountryCode": "US"
                            },
                            "Phone": {
                                "Number": integration.order.phone_number
                            }
                        },
                        "Service": {
                            "Code": "03",  # UPS Ground
                            "Description": "UPS Ground"
                        },
                        "Package": {
                            "PackagingType": {
                                "Code": "02",  # Customer Supplied Package
                                "Description": "Customer Supplied Package"
                            },
                            "Dimensions": {
                                "UnitOfMeasurement": {
                                    "Code": "IN",
                                    "Description": "Inches"
                                },
                                "Length": "10",
                                "Width": "8",
                                "Height": "6"
                            },
                            "PackageWeight": {
                                "UnitOfMeasurement": {
                                    "Code": "LBS",
                                    "Description": "Pounds"
                                },
                                "Weight": "1.0"
                            }
                        }
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracking_number = data.get('ShipmentResponse', {}).get('ShipmentResults', {}).get('ShipmentIdentificationNumber')
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'UPS API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error creating UPS shipment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_ups_access_token(self) -> str:
        """
        Get UPS API access token
        
        Returns:
            Access token string
        """
        try:
            url = "https://onlinetools.ups.com/security/v1/oauth/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials'
            }
            
            # Basic auth with username and password
            auth = (self.ups_username, self.ups_password)
            
            response = requests.post(url, headers=headers, data=data, auth=auth, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token', '')
            else:
                logger.error(f"Error getting UPS access token: {response.text}")
                return ''
                
        except Exception as e:
            logger.error(f"Error getting UPS access token: {str(e)}")
            return ''
    
    def create_aramex_shipment(self, integration: ShippingIntegration) -> Dict[str, Any]:
        """
        Create a shipment with Aramex
        
        Args:
            integration: ShippingIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.aramex_account_pin, self.aramex_account_number, self.aramex_account_entity, self.aramex_account_country_code]):
            return {
                'success': False,
                'error': 'Aramex API credentials not configured'
            }
            
        try:
            # Aramex API endpoint
            url = "https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments"
            
            # Request payload - simplified for demonstration
            payload = {
                "Shipments": {
                    "Shipment": {
                        "Shipper": {
                            "Reference1": "Store Reference",
                            "AccountNumber": self.aramex_account_number,
                            "PartyAddress": {
                                "Line1": "Store Address Line 1",
                                "City": "Store City",
                                "PostalCode": "12345",
                                "CountryCode": "US"
                            },
                            "Contact": {
                                "PersonName": "Store Owner",
                                "PhoneNumber1": "1234567890"
                            }
                        },
                        "Consignee": {
                            "Reference1": "Customer Reference",
                            "PartyAddress": {
                                "Line1": integration.order.shipping_address,
                                "City": "Customer City",
                                "PostalCode": "54321",
                                "CountryCode": "US"
                            },
                            "Contact": {
                                "PersonName": "Customer Name",
                                "PhoneNumber1": integration.order.phone_number
                            }
                        },
                        "Details": {
                            "Dimensions": {
                                "Length": "10.0",
                                "Width": "8.0",
                                "Height": "6.0",
                                "Unit": "CM"
                            },
                            "ActualWeight": {
                                "Value": "1.0",
                                "Unit": "KG"
                            },
                            "ProductGroup": "EXP",
                            "ProductType": "PDX",
                            "PaymentType": "P",
                            "NumberOfPieces": "1"
                        }
                    }
                },
                "ClientInfo": {
                    "AccountCountryCode": self.aramex_account_country_code,
                    "AccountEntity": self.aramex_account_entity,
                    "AccountNumber": self.aramex_account_number,
                    "AccountPin": self.aramex_account_pin,
                    "UserName": "testapi@aramex.com",
                    "Password": "R123456789$r",
                    "Version": "1.0"
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tracking_number = data.get('Shipments', {}).get('Shipment', {}).get('ID')
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'Aramex API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error creating Aramex shipment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_shipment(self, integration: ShippingIntegration) -> Dict[str, Any]:
        """
        Create a shipment with the specified shipping provider
        
        Args:
            integration: ShippingIntegration instance
            
        Returns:
            Dictionary with success status and response data
        """
        if integration.provider == 'fedex':
            return self.create_fedex_shipment(integration)
        elif integration.provider == 'dhl':
            return self.create_dhl_shipment(integration)
        elif integration.provider == 'ups':
            return self.create_ups_shipment(integration)
        elif integration.provider == 'aramex':
            return self.create_aramex_shipment(integration)
        else:
            return {
                'success': False,
                'error': f'Unsupported shipping provider: {integration.provider}'
            }

# Singleton instance for easy access
shipping_service = ShippingService()