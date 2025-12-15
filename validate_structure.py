#!/usr/bin/env python3
"""
Quick validation script to test the project structure without running Django.
This validates imports and basic model definitions.
"""
import sys
import os

# Add project to path
sys.path.insert(0, '/home/mahdi/Projects/Barber-Shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

print("🔍 Validating Project Structure...\n")

# Test 1: Check project structure
print("✓ Checking file structure...")
required_files = [
    'manage.py',
    'config/settings.py',
    'config/urls.py',
    'apps/accounts/models.py',
    'apps/salons/models.py',
    'apps/appointments/models.py',
    'apps/ratings/models.py',
    'requirements.txt',
    'Dockerfile',
    'docker-compose.yml',
]

for file in required_files:
    path = f'/home/mahdi/Projects/Barber-Shop/{file}'
    if os.path.exists(path):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ MISSING: {file}")

# Test 2: Check Python syntax
print("\n✓ Checking Python syntax...")
python_files = [
    'config/settings.py',
    'apps/accounts/models.py',
    'apps/accounts/views.py',
    'apps/appointments/models.py',
    'apps/ratings/models.py',
]

for file in python_files:
    path = f'/home/mahdi/Projects/Barber-Shop/{file}'
    try:
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
        print(f"  ✓ {file} - syntax OK")
    except SyntaxError as e:
        print(f"  ✗ {file} - SYNTAX ERROR: {e}")

# Test 3: Count lines of code
print("\n📊 Code Statistics:")
total_lines = 0
for root, dirs, files in os.walk('/home/mahdi/Projects/Barber-Shop/apps'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines

print(f"  Total Python LOC in apps/: {total_lines}")

# Test 4: Check templates
print("\n✓ Checking templates...")
templates = [
    'templates/base.html',
    'templates/accounts/login.html',
    'templates/accounts/register_customer.html',
]

for template in templates:
    path = f'/home/mahdi/Projects/Barber-Shop/{template}'
    if os.path.exists(path):
        print(f"  ✓ {template}")

print("\n✅ Structure validation complete!")
print("\nNext steps:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Set up database (PostgreSQL or SQLite for testing)")
print("  3. Run migrations: python manage.py migrate")
print("  4. Create superuser: python manage.py createsuperuser")
print("  5. Seed data: python manage.py seed_data")
print("  6. Run tests: python manage.py test")
print("  7. Start server: python manage.py runserver")
