#!/usr/bin/env python
"""
Script to verify that all required dependencies are installed correctly.
"""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        package = package_name or module_name
        print(f"✗ {module_name} is NOT installed (pip install {package})")
        return False

def main():
    print("Checking MyShop dependencies...\n")
    
    # Core dependencies
    dependencies = [
        ("django", "Django"),
        ("PIL", "Pillow"),
        ("colorfield", "django-colorfield"),
        ("stripe", "stripe"),
        ("paypalrestsdk", "paypalrestsdk"),
        ("rest_framework", "djangorestframework"),
        ("corsheaders", "django-cors-headers"),
        ("pytest", "pytest"),
        ("pytest_django", "pytest-django"),
        ("pytest_cov", "pytest-cov"),
    ]
    
    all_good = True
    for module, package in dependencies:
        if not check_import(module, package):
            all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("✓ All dependencies are installed correctly!")
        print("\nYou can now run tests with: pytest")
    else:
        print("✗ Some dependencies are missing!")
        print("\nInstall missing dependencies with: pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)