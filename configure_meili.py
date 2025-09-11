import meilisearch

def main():
    print("Connecting to MeiliSearch...")
    client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')
    index = client.index('products')
    
    print("Updating ALL index settings (Searchable, Filterable, Sortable)...")
    
    # 1. تعریف ویژگی‌های قابل جستجو (Searchable Attributes)
    # به ترتیب اولویت: ابتدا نام محصول، سپس تگ‌ها و برند.
    index.update_searchable_attributes([
        'product_name',
        'brand_name',
        'tags',
        'cpu_model',
        'processor_tier'
    ])

    # 2. تعریف ویژگی‌های قابل فیلتر (Filterable Attributes)
    index.update_filterable_attributes([
        'brand_name', 
        'price',
        'average_score',
        'processor_brand',
        'ram_memory',
        'primary_storage_capacity',
        'gpu_type',
        'display_size',
        'is_touch_screen',
        'os',
        'gpu_vram_gb'
    ])

    # 3. تعریف ویژگی‌های قابل مرتب‌سازی (Sortable Attributes)
    index.update_sortable_attributes([
        'price',
        'average_score',
        'ram_memory',
        'primary_storage_capacity',
        'gpu_vram_gb'
    ])

    print("MeiliSearch settings updated successfully.")

if __name__ == '__main__':
    main()