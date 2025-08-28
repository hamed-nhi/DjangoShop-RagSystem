# apps/ai_assistant/management/commands/index_to_meili.py

import meilisearch
from django.core.management.base import BaseCommand
from apps.products.models import Product
from tqdm import tqdm
from .create_faiss_index import generate_tags, clean_text # توابع کمکی را از اسکریپت قبلی وارد می‌کنیم

class Command(BaseCommand):
    help = 'Indexes all products from PostgreSQL to MeiliSearch with rich data.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Connecting to MeiliSearch server...")
        client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')

        index = client.index('products')
        self.stdout.write("Setting up MeiliSearch index configurations...")
        
        # --- تنظیمات ایندکس: تعریف فیلدهای قابل فیلتر و مرتب‌سازی ---
        index.update_settings({
            'filterableAttributes': ['price', 'brand_name', 'tags', 'average_score'],
            'sortableAttributes': ['price', 'average_score'],
            'searchableAttributes': ['product_name', 'brand_name', 'tags', 'features_flat', 'description']
        })
        self.stdout.write("Index settings updated successfully.")

        products = list(Product.objects.filter(is_active=True).select_related('brand').prefetch_related('product_features__feature'))
        if not products:
            self.stdout.write(self.style.WARNING("No active products found to index."))
            return

        self.stdout.write(f"Preparing {len(products)} product documents for indexing...")
        documents = []
        for product in tqdm(products, desc="Processing products"):
            tags = generate_tags(product)
            brand_name = product.brand.brand_title if product.brand else None
            
            # استخراج ویژگی‌ها به دو صورت: دیکشنری برای نمایش و متن برای جستجو
            features_dict = {pf.feature.feature_name: pf.value for pf in product.product_features.all() if pf.value}
            features_flat = " ".join(features_dict.values())
            
            # ساختن یک سند کامل و بهینه برای MeiliSearch
            doc = {
                'id': product.id,
                'product_name': product.product_name,
                'brand_name': brand_name,
                'price': product.price,
                'image_url': product.image_name.url if product.image_name else None,
                'slug': product.slug,
                'average_score': float(product.get_average_score()), # برای فیلتر و مرتب‌سازی
                'features': features_dict,       # برای نمایش جزئیات در آینده
                'features_flat': features_flat,  # برای جستجوی بهتر
                'tags': tags,
                'description': clean_text(product.description),
            }
            documents.append(doc)

        self.stdout.write("Clearing old documents and sending new data to MeiliSearch...")
        index.delete_all_documents() # پاک کردن داده‌های قدیمی قبل از افزودن داده‌های جدید
        
        # ارسال داده‌ها در دسته‌های ۵۰۰ تایی
        for i in range(0, len(documents), 500):
            index.add_documents(documents[i:i+500])

        self.stdout.write(self.style.SUCCESS("All products have been successfully indexed in MeiliSearch!"))