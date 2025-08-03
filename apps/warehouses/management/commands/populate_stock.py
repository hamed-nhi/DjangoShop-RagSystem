# warehouse/management/commands/populate_stock.py

import random
from django.core.management.base import BaseCommand
from apps.products.models import Product
from apps.warehouses.models import Warehouse, WarehouseType
from apps.accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Populates all products with random stock levels between 20 and 100.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting to populate stock for all products...'))

        
        try:
            incoming_warehouse_type = WarehouseType.objects.get(id=1)
        except WarehouseType.DoesNotExist:
            self.stdout.write(self.style.ERROR('WarehouseType with id=1 not found. Please create it first.'))
            return

        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No superuser found to assign stock entries to. Please create a superuser.'))
            return

        products = Product.objects.all()
        product_count = products.count()
        
        if product_count == 0:
            self.stdout.write(self.style.NOTICE('No products found in the database.'))
            return

        self.stdout.write(f'Found {product_count} products. Processing...')

        for product in products:
            random_qty = random.randint(23, 106)
            
            Warehouse.objects.create(
                product=product,
                warehouse_type=incoming_warehouse_type,
                qty=random_qty,
                user_registerd=admin_user,
                price=product.price 
            )
            
            self.stdout.write(self.style.SUCCESS(f'Added {random_qty} units of stock for "{product.product_name}"'))

        self.stdout.write(self.style.SUCCESS('Successfully populated stock for all products!'))