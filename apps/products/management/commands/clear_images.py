# products/management/commands/clear_images.py
from django.core.management.base import BaseCommand
from apps.products.models import Product

class Command(BaseCommand):
    help = 'Clears the image_name field for all products.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing all product image fields...')
        # تمام محصولات را گرفته و فیلد عکس آنها را خالی می‌کند
        updated_count = Product.objects.all().update(image_name='')
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared image field for {updated_count} products.'))