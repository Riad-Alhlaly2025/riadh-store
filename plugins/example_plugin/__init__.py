"""
Example plugin for the store application.
Demonstrates how to create a plugin.
"""
from plugins.base import BasePlugin


class ExamplePlugin(BasePlugin):
    """Example plugin implementation."""
    
    def __init__(self):
        super().__init__("Example Plugin", "1.0.0")
        
    def initialize(self) -> bool:
        """Initialize the plugin."""
        print(f"Initializing {self.name} v{self.version}")
        # Add initialization logic here
        return True
    
    def cleanup(self) -> None:
        """Clean up resources."""
        print(f"Cleaning up {self.name}")


# Create an instance of the plugin
plugin = ExamplePlugin()