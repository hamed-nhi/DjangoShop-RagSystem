import os
import django
import meilisearch
import re
from tqdm import tqdm
from flashtext import KeywordProcessor

# --- تنظیمات اولیه برای دسترسی به مدل‌های جنگو ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shop.settings')
django.setup()
# ---

from apps.products.models import Product

# --- دیکشنری جامع مترادف‌ها (ادغام شده از اسکریپت Faiss شما) ---
SYNONYM_MAP = {
    'hp': ['اچ پی', 'اچ بی', 'اچپی'], 'lg': ['ال جی', 'الجی'], 'laptop': ['لپ تاپ', 'لب تاب', 'لپتاپ', 'لبتاب', 'رایانه'],
    'touchscreen': ['صفحه لمسی', 'نمایشگر لمسی', 'مانیتور لمسی', 'لمسی', 'لمس', 'touch'],
    'graphics': ['گرافیک', 'کارت گرافیک', 'پردازشگر گرافیکی', 'جیفورس', 'جی فورس', 'gpu'],
    'professional': ['حرفه ای', 'حرفه', 'متخصصی', 'workstation', 'business'],
    'asus': ['ایسوس', 'اسوس'], 'ryzen': ['رایزن', 'رای زن'], 'dell': ['دل'], 'acer': ['ایسر', 'ایصر','ای سر'],
    'lenovo': ['لنوو', 'لنو'], 'apple': ['اپل', 'ابل'], 'microsoft': ['مایکروسافت'],
    'surface': ['سرفیس', 'سورفیس'], 'msi': ['ام اس ای', 'ام اس آی'], 'samsung': ['سامسونگ'], 'gigabyte': ['گیگابایت'],
    'amd': ['ای ام دی'], 'nvidia': ['انویدیا'], 'intel': ['اینتل'], 'processor': ['پردازنده', 'سی پی یو', 'cpu'],
    'hdd': ['هارد دیسک', 'حافظه مکانیکی','هارد'], 'ssd': ['اس اس دی', 'درایو حالت جامد'],
    'chromebook': ['کرومبوک', 'کروم بوک'], 'gaming': ['گیمینگ', 'بازی', 'مخصوص بازی', 'گیم'],
    'student': ['دانشجویی', 'مناسب دانشجو', 'دانش اموز', 'education'],
    'office': ['اداری', 'کاری'], 'budget': ['ارزان', 'اقتصادی', 'کم هزینه', 'economy', 'affordable'],
    'vivobook': ['ویوبوک','ویووبوک'], 'zenbook': ['زنبوک'], 'tuf': ['تاف', 'تی یو اف'], 'rog': ['راگ', 'آر او جی'],
    'mainstream': ['میان رده', 'نیمه حرفه ای', 'mainstream'],
    'xps': ['ایکس پی اس'], 'inspiron': ['اینسپایرون', 'اینسپایرن'], 'alienware': ['الین ویر', 'الینویر'],
    'thinkpad': ['ثینکپد', 'تینک پد', 'سینک پد'], 'ideapad': ['ایدیاپد', 'ایدیا پد'], 'yoga': ['یوگا'],
    'legion': ['لیجن', 'لژیون'], 'spectre': ['اسپکتر'], 'envy': ['انوی'], 'pavilion': ['پاویلیون'],
    'omen': ['اومن'], 'aspire': ['اسپایر'], 'predator': ['پردیتور', 'پریدیتور'], 'nitro': ['نایترو', 'نیترو'],
    'cyborg': ['سایبورگ'], 'katana': ['کاتانا'], 'stealth': ['استیلث'], 'macbook': ['مکبوک', 'مک بوک'],
    'galaxybook': ['گلکسی بوک'], 'geforce': ['جیفورس', 'جی فورس'],
    'portable': ['قابل حمل', 'سبک', 'lightweight', 'thin and light'],
    'high-performance': ['عملکرد بسیار بالا', 'قدرتمند', 'powerful'],
}

synonym_processor = KeywordProcessor()
synonym_processor.add_keywords_from_dict(SYNONYM_MAP)

def expand_with_synonyms(text: str) -> str:
    if not text: return ""
    # Using a simple space replacement for flashtext compatibility
    normalized_text = text.replace('‌', ' ') # Replace half-space with space
    return synonym_processor.replace_keywords(normalized_text)

def generate_tags(price, features):
    tags = set()
    processor = features.get('processor_tier', 'other')
    ram = int(features.get('ram_memory', '0'))
    gpu_type = features.get('gpu_type')
    display_size = float(features.get('display_size', '15.6'))
    score = 0
    cpu_scores = {'celeron': 1, 'pentium': 1, 'core i3': 2, 'ryzen 3': 2, 'core i5': 3, 'ryzen 5': 3, 'core i7': 4, 'ryzen 7': 4, 'core ultra 7': 4, 'm1': 4, 'm2': 5, 'm3': 5, 'core i9': 5, 'ryzen 9': 5}
    score += cpu_scores.get(processor, 2)
    if ram >= 32: score += 4
    elif ram >= 16: score += 3
    elif ram >= 8: score += 2
    else: score += 1
    if gpu_type == 'dedicated': score += 3
    else: score += 1
    
    LOW_PRICE_BRACKET, MID_PRICE_BRACKET = 30_000_000, 70_000_000
    LOW_PERF_SCORE, MID_PERF_SCORE, HIGH_PERF_SCORE = 4, 7, 8
    
    # --- Rich & Bilingual Tagging Logic ---
    if price < LOW_PRICE_BRACKET:
        tags.update(["پایین رده", "budget", "اقتصادی", "economy"])
    elif price < MID_PRICE_BRACKET:
        tags.update(["میان رده", "mainstream"])
    else:
        tags.update(["بالارده", "high-end", "Premium"])

    if score >= HIGH_PERF_SCORE:
        tags.update(["حرفه‌ای", "professional", "workstation", "business", "عملکرد بسیار بالا", "high-performance", "قدرتمند", "powerful"])

    if score >= MID_PERF_SCORE and price < MID_PRICE_BRACKET:
        tags.update(["ارزش خرید بالا", "high-value"])

    if score >= 5 and price < (MID_PRICE_BRACKET - 15_000_000):
        tags.update(["دانشجویی", "student", "education"])

    if gpu_type == 'dedicated':
        tags.update(["گیمینگ", "gaming", "بازی", "game"])
        if ram >= 16 and score >= HIGH_PERF_SCORE:
            tags.update(["مناسب تدوین و طراحی", "design-editing", "مناسب مهندسی", "engineering"])

    if features.get('gpu_brand') == 'nvidia' and gpu_type == 'dedicated' and ram >= 16:
        tags.update(["مناسب هوش مصنوعی", "ai-ready"])

    if ram >= 16 or (ram >= 8 and score >= 5):
        tags.update(["مناسب برنامه نویسی", "programming", "developer"])

    if display_size <= 14.0:
        tags.update(["سبک و قابل حمل", "portable", "lightweight", "thin and light"])

    if features.get('is_touch_screen', 'false').lower() == 'true':
        tags.update(["صفحه لمسی", "touchscreen", "touch"])

    if not tags:
        tags.update(["کاربری عمومی", "general-use"])
        
    return list(tags)

def prepare_product_document(product: Product) -> dict:
    document = {
        'id': product.id,
        'product_name': expand_with_synonyms(product.product_name), #<-- Enriched Product Name
        'brand_name': product.brand.brand_title.lower() if product.brand else None,
        'price': product.price,
        'image_url': product.image_name.url if product.image_name else None,
        'slug': product.slug,
        'average_score': float(product.get_average_score()),
    }
    
    features_dict = {pf.feature.feature_name.lower(): pf.value for pf in product.product_features.all()}
    document['tags'] = generate_tags(product.price, features_dict) #<-- Rich Tags

    gpu_vram_gb = None
    if features_dict.get('gpu_type') == 'dedicated':
        vram_from_name = 0
        match = re.search(r'(\d+)\s*GB Graph', product.product_name, re.IGNORECASE)
        if match:
            try: vram_from_name = int(match.group(1))
            except (ValueError, TypeError): pass
        if vram_from_name > 0: gpu_vram_gb = vram_from_name
    document['gpu_vram_gb'] = gpu_vram_gb
    
    for feature_name, value in features_dict.items():
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
    print("Connecting to MeiliSearch...")
    client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')
    index = client.index('products')
    print("Fetching all products from the database...")
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