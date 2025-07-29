# apps/products/management/commands/update_prices.py

import math
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product

class Command(BaseCommand):
    help = 'Increases and charms the prices for all products'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting to update product prices...")

        products_to_update = []
        all_products = Product.objects.all()

        for p in all_products:
            # مرحله ۱: افزایش قیمت به صورت تصادفی بین ۵ تا ۸ میلیون
            increase_amount = random.randint(5000000, 8000000)
            new_base_price = p.price + increase_amount

            # مرحله ۲: جذاب‌سازی قیمت جدید
            final_price = 0
            if new_base_price < 100000:
                rounded_up = math.ceil(new_base_price / 10000) * 10000
                final_price = rounded_up - 100
            else:
                rounded_up = math.ceil(new_base_price / 100000) * 100000
                final_price = rounded_up - 1000
            
            # قیمت نهایی را در فیلد قیمت محصول ذخیره می‌کنیم
            p.price = final_price
            products_to_update.append(p)

        # برای سرعت بیشتر و اطمینان از صحت، تمام تغییرات را به صورت یکجا در دیتابیس اعمال می‌کنیم
        Product.objects.bulk_update(products_to_update, ['price'])

        self.stdout.write(self.style.SUCCESS(f"Successfully updated prices for {len(products_to_update)} products."))
