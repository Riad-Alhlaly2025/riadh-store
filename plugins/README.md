# Plugin System Documentation

## Overview
The plugin system allows developers to extend the functionality of the store application without modifying the core codebase.

## Creating a Plugin

1. Create a new directory in the `plugins` folder with your plugin name
2. Create an `__init__.py` file in your plugin directory
3. Inherit from the `BasePlugin` class
4. Implement the required methods

## Example Plugin

```python
from plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__("My Plugin", "1.0.0")
        
    def initialize(self) -> bool:
        # Initialization logic here
        return True
    
    def cleanup(self) -> None:
        # Cleanup logic here
        pass

# Create an instance
plugin = MyPlugin()
```

## Plugin Hooks

Plugins can register for various hooks in the application:

- `on_startup`: Called when the application starts
- `on_shutdown`: Called when the application shuts down
- `on_user_login`: Called when a user logs in
- `on_order_created`: Called when an order is created
- `on_payment_processed`: Called when a payment is processed

## Loading Plugins

Plugins are automatically discovered and loaded at application startup.