# products/management/commands/reset_and_fill_slugs.py

import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Product

def make_clean_slug(value: str, max_length: int = 100) -> str:
    """
    1. Remove content inside parentheses (and the parentheses themselves)
    2. slugify the remainder
    3. Truncate to max_length and strip trailing hyphens
    """
    # 1. Strip out parentheses and their contents
    no_paren = re.sub(r'\s*\(.*?\)\s*', ' ', value)
    # 2. slugify
    base_slug = slugify(no_paren)
    # 3. Truncate to max_length
    if len(base_slug) > max_length:
        base_slug = base_slug[:max_length].rstrip('-')
    return base_slug

class Command(BaseCommand):
    help = 'Reset all slugs to null and refill them from product_name with a longer max_length'

    def unique_slugify(self, model_cls, base_slug: str, slug_field: str = 'slug') -> str:
        """
        Ensure slug uniqueness by appending -1, -2, ... if needed.
        """
        slug = base_slug
        num = 1
        lookup = {slug_field: slug}
        while model_cls.objects.filter(**lookup).exists():
            slug = f"{base_slug}-{num}"
            lookup = {slug_field: slug}
            num += 1
        return slug

    def handle(self, *args, **options):
        # 1. Reset all slugs
        Product.objects.all().update(slug=None)
        self.stdout.write(self.style.WARNING("All existing slugs cleared."))

        # 2. Re-generate and save new slugs
        qs = Product.objects.all()
        total = qs.count()
        self.stdout.write(f"Re-populating slugs for {total} products with max_length=100...")

        for product in qs:
            base = make_clean_slug(product.product_name, max_length=100)
            final_slug = self.unique_slugify(Product, base)
            product.slug = final_slug
            product.save(update_fields=['slug'])
            self.stdout.write(self.style.SUCCESS(f"{product.product_name} → {product.slug}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done! Slugs have been reset and refilled for {total} products."
        ))
