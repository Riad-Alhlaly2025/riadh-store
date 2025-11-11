"""
Plugin Manager for the store application.
Handles loading, registering, and managing plugins.
"""
import os
import importlib
from typing import Dict, List, Any


class PluginManager:
    """Manages plugins for the store application."""
    
    def __init__(self, plugins_dir: str | None = None):
        self.plugins_dir = plugins_dir or 'plugins'
        self.plugins: Dict[str, Any] = {}
        self.loaded_plugins: List[str] = []
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory."""
        plugins = []
        if os.path.exists(self.plugins_dir):
            for item in os.listdir(self.plugins_dir):
                plugin_path = os.path.join(self.plugins_dir, item)
                if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                    plugins.append(item)
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin by name."""
        try:
            if plugin_name in self.loaded_plugins:
                return True
                
            plugin_module = importlib.import_module(f'plugins.{plugin_name}')
            self.plugins[plugin_name] = plugin_module
            self.loaded_plugins.append(plugin_name)
            return True
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        plugins = self.discover_plugins()
        for plugin in plugins:
            results[plugin] = self.load_plugin(plugin)
        return results
    
    def get_plugin(self, plugin_name: str) -> Any:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, Any]:
        """Get all loaded plugins."""
        return self.plugins
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded."""
        return plugin_name in self.loaded_plugins
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins.remove(plugin_name)
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
            return True
        return False


# Global plugin manager instance
plugin_manager = PluginManager()