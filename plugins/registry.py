"""
Plugin registry for the store application.
Manages plugin hooks and callbacks.
"""
from typing import Dict, List, Callable, Any


class PluginRegistry:
    """Registry for managing plugin hooks and callbacks."""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
        
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a callback for a specific hook."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def unregister_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a callback for a specific hook."""
        if hook_name in self.hooks:
            if callback in self.hooks[hook_name]:
                self.hooks[hook_name].remove(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook and call all registered callbacks."""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error in hook {hook_name}: {e}")
        return results
    
    def get_hooks(self, hook_name: str) -> List[Callable]:
        """Get all callbacks registered for a hook."""
        return self.hooks.get(hook_name, [])


# Global plugin registry instance
plugin_registry = PluginRegistry()