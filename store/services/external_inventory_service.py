"""
External Inventory Service Module
Provides real API connections to various external inventory systems
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from store.models import ExternalInventory, Product

logger = logging.getLogger(__name__)

class ExternalInventoryService:
    """Service class for handling external inventory system API integrations"""
    
    def __init__(self):
        # API credentials would typically be stored in Django settings
        self.erpnext_api_key = getattr(settings, 'ERPNEXT_API_KEY', None)
        self.erpnext_api_secret = getattr(settings, 'ERPNEXT_API_SECRET', None)
        self.erpnext_base_url = getattr(settings, 'ERPNEXT_BASE_URL', None)
        
        self.odoo_api_key = getattr(settings, 'ODOO_API_KEY', None)
        self.odoo_db_name = getattr(settings, 'ODOO_DB_NAME', None)
        self.odoo_base_url = getattr(settings, 'ODOO_BASE_URL', None)
        
        self.sap_api_key = getattr(settings, 'SAP_API_KEY', None)
        self.sap_base_url = getattr(settings, 'SAP_BASE_URL', None)
    
    def sync_with_erpnext(self, inventory: ExternalInventory) -> Dict[str, Any]:
        """
        Sync inventory with ERPNext
        
        Args:
            inventory: ExternalInventory instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.erpnext_api_key, self.erpnext_api_secret, self.erpnext_base_url]):
            return {
                'success': False,
                'error': 'ERPNext API credentials not configured'
            }
            
        try:
            # ERPNext API endpoint for item details
            url = f"{self.erpnext_base_url}/api/resource/Item/{inventory.external_id}"
            
            # Headers
            headers = {
                'Authorization': f'token {self.erpnext_api_key}:{self.erpnext_api_secret}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                erpnext_stock = data.get('data', {}).get('opening_stock', 0)
                
                return {
                    'success': True,
                    'stock': erpnext_stock,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'ERPNext API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error syncing with ERPNext: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_with_odoo(self, inventory: ExternalInventory) -> Dict[str, Any]:
        """
        Sync inventory with Odoo
        
        Args:
            inventory: ExternalInventory instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.odoo_api_key, self.odoo_db_name, self.odoo_base_url]):
            return {
                'success': False,
                'error': 'Odoo API credentials not configured'
            }
            
        try:
            # Odoo API endpoint for product details
            url = f"{self.odoo_base_url}/jsonrpc"
            
            # Headers
            headers = {
                'Content-Type': 'application/json'
            }
            
            # First authenticate
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "login",
                    "args": [self.odoo_db_name, self.odoo_api_key, ""]
                },
                "id": 1
            }
            
            auth_response = requests.post(url, headers=headers, json=auth_payload, timeout=30)
            
            if auth_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Odoo authentication error: {auth_response.text}'
                }
            
            auth_data = auth_response.json()
            uid = auth_data.get('result')
            
            if not uid:
                return {
                    'success': False,
                    'error': 'Odoo authentication failed'
                }
            
            # Now get product details
            product_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        self.odoo_db_name,
                        uid,
                        self.odoo_api_key,
                        'product.product',
                        'read',
                        [int(inventory.external_id)],
                        ['qty_available', 'incoming_qty', 'outgoing_qty']
                    ]
                },
                "id": 2
            }
            
            product_response = requests.post(url, headers=headers, json=product_payload, timeout=30)
            
            if product_response.status_code == 200:
                product_data = product_response.json()
                product_info = product_data.get('result', [{}])[0] if product_data.get('result') else {}
                odoo_stock = product_info.get('qty_available', 0)
                
                return {
                    'success': True,
                    'stock': odoo_stock,
                    'response': product_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Odoo API error: {product_response.text}',
                    'status_code': product_response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error syncing with Odoo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_with_sap(self, inventory: ExternalInventory) -> Dict[str, Any]:
        """
        Sync inventory with SAP
        
        Args:
            inventory: ExternalInventory instance
            
        Returns:
            Dictionary with success status and response data
        """
        if not all([self.sap_api_key, self.sap_base_url]):
            return {
                'success': False,
                'error': 'SAP API credentials not configured'
            }
            
        try:
            # SAP API endpoint for material details
            url = f"{self.sap_base_url}/sap/opu/odata/sap/API_PRODUCT_READ_SRV/A_Product('{inventory.external_id}')"
            
            # Headers
            headers = {
                'Authorization': f'Bearer {self.sap_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                sap_stock = data.get('d', {}).get('ProductStock', 0)
                
                return {
                    'success': True,
                    'stock': sap_stock,
                    'response': data
                }
            else:
                return {
                    'success': False,
                    'error': f'SAP API error: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error syncing with SAP: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_inventory(self, inventory: ExternalInventory) -> Dict[str, Any]:
        """
        Sync inventory with the specified external system
        
        Args:
            inventory: ExternalInventory instance
            
        Returns:
            Dictionary with success status and response data
        """
        if inventory.system_name.lower() == 'erpnext':
            return self.sync_with_erpnext(inventory)
        elif inventory.system_name.lower() == 'odoo':
            return self.sync_with_odoo(inventory)
        elif inventory.system_name.lower() == 'sap':
            return self.sync_with_sap(inventory)
        else:
            return {
                'success': False,
                'error': f'Unsupported inventory system: {inventory.system_name}'
            }

# Singleton instance for easy access
external_inventory_service = ExternalInventoryService()