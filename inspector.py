# inspector.py (Corrected Version)
import meilisearch

# --- CONFIGURATION ---
MEILI_URL = 'http://127.0.0.1:7700'
MEILI_API_KEY = 'MASTER_KEY'
INDEX_NAME = 'products'

# <<-- شناسه محصولی که مطمئنید باید "حرفه‌ای" باشد را اینجا وارد کنید
PRODUCT_ID_TO_INSPECT = 448 #<-- این عدد را با شناسه محصول مورد نظر خود تغییر دهید

def inspect_product():
    """تگ‌های یک محصول مشخص را مستقیماً از Meilisearch می‌خواند."""
    try:
        client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)
        index = client.index(INDEX_NAME)
        print(f"🔎 در حال بازرسی تگ‌های محصول با شناسه: {PRODUCT_ID_TO_INSPECT}")
        
        product = index.get_document(PRODUCT_ID_TO_INSPECT)
        
        # --- FIX: Correct way to access tags ---
        if hasattr(product, 'tags'):
            tags = product.tags
        else:
            tags = 'فیلد تگ برای این محصول وجود ندارد'
        # --- END FIX ---

        print("\n" + "="*50)
        print("✅ تگ‌های ثبت‌شده در Meilisearch برای این محصول:")
        print(tags)
        print("="*50)

    except Exception as e:
        print(f"\n❌ خطایی رخ داد: {e}")
        print("لطفاً مطمئن شوید شناسه محصول صحیح است و در Meilisearch وجود دارد.")

if __name__ == '__main__':
    inspect_product()