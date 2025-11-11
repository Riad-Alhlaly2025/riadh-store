# Script to extract clean content from the backup file

with open('store/views.py.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position of the debug_manager_access function
pos = content.rfind('def debug_manager_access')

# Extract the clean content up to that position
clean_content = content[:pos]

# Write to a new file
with open('store/views_clean.py', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("Successfully extracted clean content to views_clean.py!")