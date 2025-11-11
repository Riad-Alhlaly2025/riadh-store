"""
Base plugin class for the store application.
All plugins should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when plugin is unloaded."""
        pass
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self.enabled
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled
        }