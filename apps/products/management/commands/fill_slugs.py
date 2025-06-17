# products/management/commands/fill_slugs.py

import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Product

def make_clean_slug(value: str, max_length: int = 50) -> str:
    """
    1. حذف محتوای داخل پرانتز و خود پرانتزها
    2. تبدیل به slug با slugify جنگو
    3. برش به max_length و حذف خط تیره‌های انتهایی
    """
    # 1. حذف پرانتز و محتوای داخل آن
    no_paren = re.sub(r'\s*\(.*?\)\s*', ' ', value)
    # 2. slugify
    base_slug = slugify(no_paren)
    # 3. برش و حذف trailing hyphens
    if len(base_slug) > max_length:
        base_slug = base_slug[:max_length].rstrip('-')
    return base_slug

class Command(BaseCommand):
    help = 'Fill missing slugs for all existing products based on cleaned product_name'

    def unique_slugify(self, model_cls, base_slug: str, slug_field: str = 'slug') -> str:
        """
        اگر slug یکتا نباشد، عدد متوالی به انتها اضافه می‌کند: 'foo', 'foo-1', 'foo-2', ...
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
        # انتخاب محصولات بدون slug
        qs = Product.objects.filter(slug__isnull=True) | Product.objects.filter(slug='')
        total = qs.count()
        self.stdout.write(f"Found {total} products without a slug.")

        for product in qs:
            # ایجاد slug اولیه
            base = make_clean_slug(product.product_name, max_length=50)
            # یکتا‌سازی
            final_slug = self.unique_slugify(Product, base)
            # ذخیره
            product.slug = final_slug
            product.save(update_fields=['slug'])
            self.stdout.write(self.style.SUCCESS(
                f"{product.product_name} → {product.slug}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Completed: slugs filled for {total} products."
        ))
