# apps/products/management/commands/rebuild_search_vectors.py

from django.core.management.base import BaseCommand
from django.db.models import Value
from django.contrib.postgres.search import SearchVector
from apps.products.models import Product

class Command(BaseCommand):
    help = 'Rebuilds the SearchVectorField for all products in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting: Script to rebuild search vectors ---'))

        products = Product.objects.select_related('brand').all()
        product_count = products.count()
        self.stdout.write(f"Found {product_count} products. Starting update process...")

        updated_count = 0
        for product in products.iterator():
            brand_title = product.brand.brand_title if product.brand else ''
            summary = product.summery_description or ''
            
            vector = (
                SearchVector('product_name', weight='A', config='simple') +
                SearchVector(Value(brand_title), weight='B', config='simple') +
                SearchVector(Value(summary), weight='C', config='simple')
            )
            
            Product.objects.filter(pk=product.pk).update(search_vector=vector)
            updated_count += 1
            
            if updated_count % 50 == 0 or updated_count == product_count:
                self.stdout.write(f"--- Updated {updated_count}/{product_count} products...")

        self.stdout.write(self.style.SUCCESS(f"--- Finished. All {product_count} products have been re-indexed."))
        self.stdout.write(self.style.SUCCESS("\n>>> Your keyword search is now optimized!"))