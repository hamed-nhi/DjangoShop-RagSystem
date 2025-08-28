# apps/ai_assistant/management/commands/create_faiss_index.py

import os
import re
import numpy as np
import faiss
import pickle
from django.core.management.base import BaseCommand
from django.conf import settings
from sentence_transformers import SentenceTransformer
from apps.products.models import Product
from tqdm import tqdm
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor

# --- دیکشنری جامع مترادف‌ها ---
SYNONYM_MAP = {
    'hp': ['اچ پی', 'اچ بی', 'اچپی'],
    'lg': ['ال جی', 'الجی'],
    'laptop': ['لپ تاپ', 'لب تاب', 'لپتاپ', 'لبتاب', 'رایانه'],
    'touchscreen': ['صفحه لمسی', 'نمایشگر لمسی', 'مانیتور لمسی', 'لمسی', 'لمس'],
    'graphics': ['گرافیک', 'کارت گرافیک', 'پردازشگر گرافیکی', 'جیفورس', 'جی فورس'],
    'professional': ['حرفه ای', 'حرفه', 'متخصصی'],
    'asus': ['ایسوس', 'اسوس'],
    'ryzen': ['رایزن', 'رای زن'],
    'dell': ['دل'],
    'acer': ['ایسر', 'ایصر','ای سر'],
    'lenovo': ['لنوو', 'لنو'],
    'apple': ['اپل', 'ابل'],
    'microsoft': ['مایکروسافت'],
    'surface': ['سرفیس', 'سورفیس'],
    'msi': ['ام اس ای', 'ام اس آی'],
    'samsung': ['سامسونگ', 'سامسنگ', 'سامسانگ'],
    'gigabyte': ['گیگابایت'],
    'amd': ['ای ام دی'],
    'nvidia': ['انویدیا'],
    'intel': ['اینتل'],
    'processor': ['پردازنده', 'سی پی یو', 'cpu'],
    'hdd': ['هارد دیسک', 'حافظه مکانیکی','هارد'],
    'ssd': ['اس اس دی', 'درایو حالت جامد'],
    'chromebook': ['کرومبوک', 'کروم بوک'],
    'gaming': ['گیمینگ', 'بازی', 'مخصوص بازی', 'گیم'],
    'student': ['دانشجویی', 'مناسب دانشجو', 'دانش اموز'],
    'office': ['اداری', 'کاری'],
    'budget': ['ارزان', 'اقتصادی', 'کم هزینه'],
      # Brands & Series
    'asus': ['ایسوس', 'اسوس'],
    'vivobook': ['ویوبوک','ویووبوک'], 
    'zenbook': ['زنبوک'], 
    'tuf': ['تاف', 'تی یو اف'],
    'rog': ['راگ', 'آر او جی'],
    'mainstrain': ['نیمه حرفه ای'],
    'dell': ['دل'],
    'xps': ['ایکس پی اس'], 
    'inspiron': ['اینسپایرون', 'اینسپایرن'],
    'alienware': ['الین ویر', 'الینویر'],

    'lenovo': ['لنوو', 'لِنوو'],
    'thinkpad': ['ثینکپد', 'تینک پد', 'سینک پد'], 
    'ideapad': ['ایدیاپد', 'ایدیا پد'], 
    'yoga': ['یوگا'],
    'legion': ['لیجن', 'لژیون'],

    'hp': ['اچ پی', 'اچ بی', 'اچپی'],
    'spectre': ['اسپکتر'],
    'envy': ['انوی'],
    'pavilion': ['پاویلیون'],
    'omen': ['اومن'],

    'acer': ['ایسر', 'ایصر'],
    'aspire': ['اسپایر'],
    'predator': ['پردیتور', 'پریدیتور'],
    'nitro': ['نایترو', 'نیترو'],

    'msi': ['ام اس ای', 'ام اس آی'],
    'cyborg': ['سایبورگ'],
    'katana': ['کاتانا'],
    'stealth': ['استیلث'],
    
    'apple': ['اپل', 'ابل'],
    'macbook': ['مکبوک', 'مک بوک'],
    
    'microsoft': ['مایکروسافت'],
    'surface': ['سرفیس', 'سِرفیس'],
    
    'samsung': ['سامسونگ', 'سامسنگ', 'سامسانگ'],
    'galaxybook': ['گلکسی بوک'],
    
    'gigabyte': ['گیگابایت'],
    'nvidia': ['انویدیا'],
    'geforce': ['جیفورس', 'جی فورس'],
    'intel': ['اینتل'],
    'ryzen': ['رایزن', 'رای زن'],
    
    # Other Brands from your list
    'honor': ['آنر'], 'realme': ['ریلمی'], 'fujitsu': ['فوجیتسو'], 'tecno': ['تکنو'], 
    'infinix': ['اینفینیکس'], 'wings': ['وینگز'], 'ultimus': ['اولتیموس'], 
    'primebook': ['پرایمبوک'], 'iball': ['آیبال'], 'zebronics': ['زبرونیکس'], 
    'chuwi': ['چووی'], 'jio': ['جیو'], 'avita': ['اویتا'], 'walker': ['واکر'], 
}


synonym_processor = KeywordProcessor()
synonym_processor.add_keywords_from_dict(SYNONYM_MAP)

def expand_with_synonyms(text: str) -> str:
    if not text: return ""
    return synonym_processor.replace_keywords(text)

def clean_text(text):
    if not text: return ""
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text()
    return re.sub(r'\s+', ' ', cleaned_text).strip()

def generate_tags(product):
    tags = set()
    features = {pf.feature.feature_name: pf.value for pf in product.product_features.select_related('feature').all()}
    processor = features.get('processor_tier', 'other')
    ram = int(features.get('ram_memory', '0'))
    gpu_type = features.get('gpu_type')
    gpu_brand = features.get('gpu_brand')
    is_touch = features.get('is_touch_screen', 'false').lower()
    display_size = float(features.get('display_size', '15.6'))
    resolution_width = int(features.get('resolution_width', '1920'))
    storage_capacity = int(features.get('primary_storage_capacity', '512'))
    secondary_storage = features.get('secondary_storage_type', 'no secondary storage')
    price = product.price
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


class Command(BaseCommand):
    help = 'Builds and saves a Faiss index for product embeddings.'
    FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, 'ai_data', 'products.faiss')
    ID_MAP_PATH = os.path.join(settings.BASE_DIR, 'ai_data', 'product_ids.pkl')
    MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

    def handle(self, *args, **kwargs):
        self.stdout.write("شروع فرآیند ساخت ایندکس Faiss...")
        os.makedirs(os.path.dirname(self.FAISS_INDEX_PATH), exist_ok=True)
        self.stdout.write(f"در حال بارگذاری مدل: {self.MODEL_NAME}...")
        model = SentenceTransformer(self.MODEL_NAME)
        self.stdout.write("مدل با موفقیت بارگذاری شد.")
        products = list(Product.objects.filter(is_active=True).select_related('brand').prefetch_related('product_features__feature'))
        if not products:
            self.stdout.write(self.style.WARNING("هیچ محصول فعالی یافت نشد."))
            return
        self.stdout.write(f"تعداد {len(products)} محصول برای پردازش یافت شد.")
        documents = []
        product_ids = []
        for product in tqdm(products, desc="ساخت اسناد متنی"):
            brand_name = product.brand.brand_title if product.brand else ""
            product_name_expanded = expand_with_synonyms(product.product_name)
            brand_name_expanded = expand_with_synonyms(brand_name)
            description_expanded = expand_with_synonyms(clean_text(product.description))
            features_parts = []
            for pf in product.product_features.all():
                if pf.value:
                    feature_name = pf.feature.feature_name
                    feature_value_expanded = expand_with_synonyms(pf.value)
                    features_parts.append(f"{feature_name}: {feature_value_expanded}")
            features_str = ". ".join(features_parts)
            generated_tags = generate_tags(product)
            tags_str = ", ".join(generated_tags)
            doc = (
                f"{product_name_expanded} برند {brand_name_expanded}. "
                f"دسته بندی: {tags_str}. "
                f"این محصول یک {expand_with_synonyms(tags_str)} است. "
                f"مشخصات: {features_str}. "
                f"توضیحات: {description_expanded}"
            )
            documents.append(doc)
            product_ids.append(product.id)

        self.stdout.write("در حال تبدیل اسناد به وکتور...")
        embeddings = model.encode(documents, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        d = embeddings.shape[1]
        self.stdout.write("در حال ساخت ایندکس Faiss...")
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        self.stdout.write(f"در حال ذخیره فایل ایندکس در: {self.FAISS_INDEX_PATH}")
        faiss.write_index(index, self.FAISS_INDEX_PATH)
        with open(self.ID_MAP_PATH, 'wb') as f:
            pickle.dump(product_ids, f)
        self.stdout.write(f"نقشه ID ها در: {self.ID_MAP_PATH} ذخیره شد.")
        self.stdout.write(self.style.SUCCESS("فرآیند با موفقیت به پایان رسید!"))
