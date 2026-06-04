import os
import sys

# Force using development settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'velora.settings.dev')

sys.path.append(os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()

def clean_and_reseed():
    print("Cleaning database of legacy mock listings and duplicates...")

    # Mock emails to purge
    mock_emails = [
        'karan.grover@gmail.com',
        'priya.sharma@gmail.com',
        'rahul.mehta@gmail.com',
        'ananya.sen@gmail.com',
        'akash.patel@gmail.com',
        'official.stores@velora.in'
    ]

    # Delete all products created by these mock sellers
    deleted_count, _ = Product.objects.filter(seller__email__in=mock_emails).delete()
    print(f"Purged {deleted_count} legacy mock products from the database.")

    # Delete test draft products
    drafts_deleted, _ = Product.objects.filter(title="Test Draft Product").delete()
    print(f"Purged {drafts_deleted} legacy test draft products.")

    # Re-run the clean seeding script
    print("Starting fresh seeding...")
    from seed_realistic_products import seed_products
    seed_products()

if __name__ == '__main__':
    clean_and_reseed()
