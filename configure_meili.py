import meilisearch

def main():
    """
    این اسکریپت برای تنظیمات اولیه و یک‌باره ایندکس محصولات در MeiliSearch است.
    """
    print("Connecting to MeiliSearch...")
    try:
        # اطلاعات اتصال به MeiliSearch خود را وارد کنید
        client = meilisearch.Client('http://127.0.0.1:7700', 'MASTER_KEY')
        
        # نام ایندکس خود را وارد کنید
        index = client.index('products')
        
        print(f"Updating filterable attributes for index '{index.uid}'...")
        
        # 'brand_name' و سایر فیلدها را به لیست ویژگی‌های قابل فیلتر اضافه کنید
        response = index.update_filterable_attributes([
            'brand_name', 
            'price',
            'average_score',
            'tags'
        ])
        
        print("Settings update task has been sent to MeiliSearch.")
        print("Task UID:", response.task_uid)
        print("Please wait a moment for the task to be processed by MeiliSearch.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()