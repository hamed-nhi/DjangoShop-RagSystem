import os
import django
import meilisearch

# --- تنظیمات اولیه برای دسترسی به مدل‌های جنگو ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shop.settings') # YOUR_PROJECT را با نام پروژه خود جایگزین کنید
django.setup()
# ---

from apps.products.models import Product
from tqdm import tqdm # یک کتابخانه زیبا برای نمایش نوار پیشرفت (با pip install tqdm نصب کنید)
def generate_tags(price, features):
    tags = set()
    processor = features.get('processor_tier', 'other')
    ram = int(features.get('ram_memory', '0'))
    gpu_type = features.get('gpu_type')
    gpu_brand = features.get('gpu_brand')
    is_touch = features.get('is_touch_screen', 'false').lower()
    display_size = float(features.get('display_size', '15.6'))
    resolution_width = int(features.get('resolution_width', '1920'))
    storage_capacity = int(features.get('primary_storage_capacity', '512'))
    secondary_storage = features.get('secondary_storage_type', 'no secondary storage')
    score = 0
    cpu_scores = {'celeron': 1, 'pentium': 1, 'core i3': 2, 'ryzen 3': 2, 'core i5': 3, 'ryzen 5': 3, 'core i7': 4, 'ryzen 7': 4, 'core ultra 7': 4, 'm1': 4, 'm2': 5, 'm3': 5, 'core i9': 5, 'ryzen 9': 5}
    score += cpu_scores.get(processor, 2)
    if ram >= 32: score += 4
    elif ram >= 16: score += 3
    elif ram >= 8: score += 2
    else: score += 1
    if gpu_type == 'dedicated': score += 3
    else: score += 1
    LOW_PRICE_BRACKET, MID_PRICE_BRACKET = 25_000_000, 60_000_000
    LOW_PERF_SCORE, MID_PERF_SCORE, HIGH_PERF_SCORE = 4, 7, 9
    if price < LOW_PRICE_BRACKET: tags.add("پایین رده")
    elif price < MID_PRICE_BRACKET: tags.add("میان رده")
    else: tags.add("بالارده"); tags.add("Premium")
    if score >= HIGH_PERF_SCORE: tags.add("حرفه‌ای"); tags.add("عملکرد بسیار بالا")
    if score >= MID_PERF_SCORE and price < MID_PRICE_BRACKET: tags.add("ارزش خرید بالا")
    if score >= 5 and price < (MID_PRICE_BRACKET - 10_000_000): tags.add("دانشجویی")
    if price < LOW_PRICE_BRACKET and score <= LOW_PERF_SCORE: tags.add("اقتصادی"); tags.add("کاربری بسیار سبک")
    if gpu_type == 'dedicated':
        tags.add("گیمینگ"); tags.add("کولینگ قوی")
        if ram >= 16 and score >= HIGH_PERF_SCORE: tags.add("مناسب تدوین و طراحی"); tags.add("مناسب مهندسی")
    if gpu_brand == 'nvidia' and gpu_type == 'dedicated' and ram >= 16: tags.add("مناسب هوش مصنوعی")
    if ram >= 16 or (ram >= 8 and score >= 5): tags.add("مناسب برنامه نویسی")
    if resolution_width >= 2560: tags.add("کیفیت صفحه نمایش عالی")
    elif resolution_width >= 1920: tags.add("کیفیت صفحه نمایش خوب")
    if display_size >= 15.6: tags.add("صفحه نمایش بزرگ")
    else: tags.add("صفحه نمایش متوسط")
    if storage_capacity >= 1024: tags.add("حافظه ذخیره سازی زیاد")
    elif storage_capacity >= 512: tags.add("حافظه ذخیره سازی مناسب")
    else: tags.add("حافظه ذخیره سازی کم")
    if secondary_storage != 'no secondary storage': tags.add("دارای حافظه مجزا")
    if is_touch == 'true': tags.add("صفحه لمسی")
    if display_size <= 14.0: tags.add("سبک و قابل حمل")
    if not tags: tags.add("کاربری عمومی")
    return list(tags)

# def prepare_product_document(product: Product) -> dict:
#     """
#     یک آبجکت محصول جنگو را به فرمت دیکشنری مسطح برای MeiliSearch تبدیل می‌کند.
#     """
#     document = {
#         'id': product.id,
#         'product_name': product.product_name,
#         'brand_name': product.brand.brand_title.lower() if product.brand else None,
#         'price': product.price,
#         'image_url': product.image_name.url if product.image_name else None,
#         'slug': product.slug,
#         'average_score': float(product.get_average_score()),
#     }
    
#     # +++ تغییر ۲: ویژگی‌ها را فقط یک بار از محصول می‌خوانیم و در یک دیکشنری ذخیره می‌کنیم +++
#     features_dict = {pf.feature.feature_name.lower(): pf.value for pf in product.product_features.all()}

#     # تگ‌ها را با استفاده از دیکشنری آماده‌شده تولید می‌کنیم
#     document['tags'] = generate_tags(product.price, features_dict)
    
#     # +++ تغییر ۳: برای مسطح‌سازی هم از همان دیکشنری آماده‌شده استفاده می‌کنیم +++
#     for feature_name, value in features_dict.items():
#         feature_name = feature_name.replace(" ", "_")
#         try:
#             if feature_name in ['ram_memory', 'primary_storage_capacity', 'num_cores', 'num_threads']:
#                 document[feature_name] = int(float(value))
#             elif feature_name in ['display_size']:
#                 document[feature_name] = float(value)
#             elif feature_name.lower() in ['is_touch_screen']:
#                 document[feature_name] = value.lower() in ('true', '1', 't', 'y', 'yes')
#             else:
#                 document[feature_name] = value.lower()
#         except (ValueError, TypeError):
#             document[feature_name] = value.lower()
            
#     return document
import re

# ... (بقیه توابع و کدها)

def prepare_product_document(product: Product) -> dict:
    """
    یک آبجکت محصول جنگو را به فرمت دیکشنری مسطح برای MeiliSearch تبدیل می‌کند.
    """
    document = {
        'id': product.id,
        'product_name': product.product_name,
        'brand_name': product.brand.brand_title.lower() if product.brand else None,
        'price': product.price,
        'image_url': product.image_name.url if product.image_name else None,
        'slug': product.slug,
        'average_score': float(product.get_average_score()),
    }
    
    features_dict = {pf.feature.feature_name.lower(): pf.value for pf in product.product_features.all()}
    document['tags'] = generate_tags(product.price, features_dict)

    # +++ رویکرد جدید و بهینه برای استخراج VRAM +++
    gpu_vram_gb = None  # 1. مقدار پیش‌فرض را None (null) قرار می‌دهیم

    # 2. فقط در صورتی به دنبال VRAM می‌گردیم که نوع گرافیک 'dedicated' باشد
    if features_dict.get('gpu_type') == 'dedicated':
        vram_from_name = 0 # مقدار موقت برای استخراج از نام
        match = re.search(r'(\d+)\s*GB Graph', product.product_name, re.IGNORECASE)
        if match:
            try:
                vram_from_name = int(match.group(1))
            except (ValueError, TypeError):
                pass
        
        # 3. اگر مقداری در نام محصول پیدا شد، آن را ثبت می‌کنیم
        if vram_from_name > 0:
            gpu_vram_gb = vram_from_name
            
    document['gpu_vram_gb'] = gpu_vram_gb
    
    # --- مسطح‌سازی بقیه ویژگی‌ها ---
    for feature_name, value in features_dict.items():
        # ... (بقیه این حلقه بدون تغییر باقی می‌ماند)
        feature_name = feature_name.replace(" ", "_")
        try:
            if feature_name in ['ram_memory', 'primary_storage_capacity', 'num_cores', 'num_threads']:
                document[feature_name] = int(float(value))
            elif feature_name in ['display_size']:
                document[feature_name] = float(value)
            elif feature_name.lower() in ['is_touch_screen']:
                document[feature_name] = value.lower() in ('true', '1', 't', 'y', 'yes')
            else:
                document[feature_name] = value.lower()
        except (ValueError, TypeError):
            document[feature_name] = value.lower()
            
    return document

def main():
    """
    تمام محصولات را از دیتابیس خوانده، به فرمت جدید تبدیل کرده و در MeiliSearch ایندکس می‌کند.
    """
    print("Connecting to MeiliSearch...")
    client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')
    index = client.index('products')

    print("Fetching all products from the database...")
    # prefetch_related همچنان بسیار مهم است و درخواست‌های دیتابیس را بهینه می‌کند
    all_products = Product.objects.all().prefetch_related('brand', 'product_features__feature')

    documents_to_index = []
    print("Preparing documents for indexing...")
    for product in tqdm(all_products, desc="Processing products"):
        documents_to_index.append(prepare_product_document(product))

    if not documents_to_index:
        print("No products found to index.")
        return

    print(f"\nSending {len(documents_to_index)} documents to MeiliSearch...")
    task = index.add_documents(documents_to_index)
    print("Documents have been sent. Task info:", task)
    print("Please wait for MeiliSearch to complete the indexing process.")

if __name__ == '__main__':
    main()