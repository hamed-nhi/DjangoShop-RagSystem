# warehouse/management/commands/update_stock_prices.py

from django.core.management.base import BaseCommand
from apps.warehouses.models import Warehouse

class Command(BaseCommand):
    help = 'Updates the price of incoming stock entries to be 95% of the product selling price.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting to update stock purchase prices...'))

        incoming_entries = Warehouse.objects.filter(warehouse_type_id=1)
        
        if not incoming_entries.exists():
            self.stdout.write(self.style.NOTICE('No incoming stock entries found to update.'))
            return

        updated_count = 0
        for entry in incoming_entries:
            selling_price = entry.product.price
            
            
            purchase_price = int(selling_price * 0.96)
            
            entry.price = purchase_price
            entry.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated the price for {updated_count} stock entries!'))