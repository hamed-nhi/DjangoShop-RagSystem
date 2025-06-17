from django.core.management.base import BaseCommand
from apps.products.models import Brand, Feature, ProductGroup, Product, ProductFeature
import pandas as pd

class Command(BaseCommand):
    help = 'وارد کردن داده‌های لپ‌تاپ از فایل CSV به دیتابیس'

    def handle(self, *args, **kwargs):
        PRODUCT_GROUP_NAME = "لپ‌تاپ"
        df = pd.read_csv('cleaned_laptops_final.csv')  # یا مسیر دقیق فایل

        try:
            product_group = ProductGroup.objects.get(group_title=PRODUCT_GROUP_NAME)
        except ProductGroup.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ گروه کالا با عنوان '{PRODUCT_GROUP_NAME}' پیدا نشد."))
            return

        for brand_title in df['brand'].dropna().unique():
            Brand.objects.get_or_create(brand_title=brand_title)

        reserved_fields = ['brand', 'product_name', 'price', 'description', 'group']
        feature_columns = [col for col in df.columns if col not in reserved_fields]

        for feature_name in feature_columns:
            feature, created = Feature.objects.get_or_create(feature_name=feature_name)
            if product_group not in feature.product_group.all():
                feature.product_group.add(product_group)

        for _, row in df.iterrows():
            brand, _ = Brand.objects.get_or_create(brand_title=row['brand'])

            product = Product.objects.create(
                product_name=row['product_name'],
                price=row.get('price', 0),
                description=row.get('description', ''),
                brand=brand,
            )
            product.product_group.add(product_group)

            for feature_name in feature_columns:
                value = row.get(feature_name)
                if pd.isna(value) or value == '':
                    continue
                try:
                    feature = Feature.objects.get(feature_name=feature_name)
                    ProductFeature.objects.create(
                        product=product,
                        feature=feature,
                        value=str(value)
                    )
                except Feature.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Feature '{feature_name}' not found."))

        self.stdout.write(self.style.SUCCESS("✅ وارد کردن اطلاعات با موفقیت انجام شد."))
