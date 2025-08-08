# apps/products/management/commands/update_vectors.py

from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from apps.products.models import Product
from django.db.models.functions import Coalesce
from django.db.models import Value

class Command(BaseCommand):
    help = 'Updates the search_vector field for all products using the "simple" config.'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS('Starting to update search vectors with "simple" config...')
        )

        # +++ Change: Added config='simple' to all SearchVector instances +++
        vector = (
            SearchVector('product_name', weight='A', config='simple') +
            SearchVector(Coalesce('brand__brand_title', Value('')), weight='B', config='simple') +
            SearchVector(Coalesce('summery_description', Value('')), weight='C', config='simple')
        )

        updated_count = Product.objects.update(search_vector=vector)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated search vectors for {updated_count} products.')
        )