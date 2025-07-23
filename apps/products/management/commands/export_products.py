# apps/products/management/commands/export_products.py
import csv
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.products.models import Product

class Command(BaseCommand):
    help = 'Exports products that need descriptions to a CSV file.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to export products...'))

        products_to_export = Product.objects.filter(
            Q(description__isnull=True) | Q(description__exact='') | Q(description__icontains='lorem')
        )

        if not products_to_export.exists():
            self.stdout.write(self.style.WARNING('No products to export.'))
            return

        file_path = 'products_to_process.csv'

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'product_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for product in products_to_export:
                writer.writerow({'id': product.id, 'product_name': product.product_name})

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {products_to_export.count()} products to "{file_path}"'))