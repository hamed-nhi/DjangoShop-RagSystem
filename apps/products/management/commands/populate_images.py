# import time
# import random
# import requests
# import os
# from django.core.management.base import BaseCommand
# from django.conf import settings
# from apps.products.models import Product

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup

# class Command(BaseCommand):
#     help = 'Scrapes and saves images for products that do not have one.'

#     def handle(self, *args, **kwargs):
#         self.stdout.write(self.style.SUCCESS('Starting to scrape images using Selenium...'))

#         # --- راه‌اندازی مرورگر کروم ---
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')  # اجرا در پشت صحنه
#         options.add_argument('--disable-gpu')
#         options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
        
#         try:
#             driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#             self.stdout.write(self.style.SUCCESS('Chrome driver started successfully.'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"Could not start Chrome driver. Error: {e}"))
#             return

#         # --- گرفتن لیست محصولات بدون عکس ---
#         products_without_images = Product.objects.filter(image_name__in=['', None])
#         total_products = products_without_images.count()
#         self.stdout.write(f'Found {total_products} products without images.')

#         # --- مسیر ذخیره عکس‌ها ---
#         image_dir = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'products')
#         if not os.path.exists(image_dir):
#             os.makedirs(image_dir)

#         # --- شروع حلقه برای هر محصول ---
#         for i, product in enumerate(products_without_images):
#             try:
#                 search_term = f"{product.product_name} laptop"
#                 self.stdout.write(f'({i+1}/{total_products}) Searching for: "{search_term}"')
                
#                 search_url = f"https://duckduckgo.com/?q={search_term.replace(' ', '+')}&t=h_&iax=images&ia=images"
                
#                 driver.get(search_url)
#                 # زمان انتظار برای لود کامل صفحه (خصوصا عکس‌ها)
#                 time.sleep(random.uniform(2.5, 4.5))

#                 # استفاده از BeautifulSoup برای پارس کردن محتوای صفحه
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')

#                 # *** سلکتور جدید و اصلاح شده ***
#                 image_tag = soup.select_one('div[data-testid="zci-images"] img')

#                 if image_tag and image_tag.has_attr('src'):
#                     image_url = image_tag['src']
                    
#                     # اطمینان از کامل بودن URL
#                     if image_url.startswith('//'):
#                         image_url = 'https:' + image_url
                    
#                     # دانلود عکس
#                     response = requests.get(image_url, stream=True, timeout=10)
#                     if response.status_code == 200:
#                         # ساختن نام فایل و ذخیره آن
#                         image_filename = f"{product.id}.jpg" 
#                         image_path = os.path.join(image_dir, image_filename)
                        
#                         with open(image_path, 'wb') as f:
#                             f.write(response.content)
                        
#                         # آپدیت مدل محصول
#                         product.image_name = image_filename
#                         product.save()
#                         self.stdout.write(self.style.SUCCESS(f'Successfully downloaded and saved {image_filename} for "{product.product_name}"'))
#                     else:
#                         self.stdout.write(self.style.WARNING(f'Failed to download image from {image_url}. Status code: {response.status_code}'))
#                 else:
#                     self.stdout.write(self.style.WARNING(f'No image found for "{product.product_name}"'))

#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'An error occurred for product ID {product.id}: {e}'))
#                 # در صورت بروز خطا، ادامه می‌دهیم تا اسکریپت متوقف نشود
#                 continue
            
#             # یک تاخیر تصادفی بین درخواست‌ها برای جلوگیری از بلاک شدن
#             if i < total_products - 1:
#                 wait_time = random.uniform(2.0, 5.0)
#                 self.stdout.write(f'Waiting for {wait_time:.2f} seconds...')
#                 time.sleep(wait_time)

#         # بستن مرورگر در انتها
#         driver.quit()
#         self.stdout.write(self.style.SUCCESS('Finished processing all products.'))





import time
import random
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.products.models import Product

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Uses Selenium to fetch and save product images correctly.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to scrape images using Selenium...'))
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
        
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            self.stdout.write(self.style.SUCCESS('Chrome driver started successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Could not start driver. Error: {e}"))
            return

        products_without_images = Product.objects.filter(image_name__in=['', None])
        total_products = products_without_images.count()
        self.stdout.write(f'Found {total_products} products without images.')

        for i, product in enumerate(products_without_images):
            try:
                search_term = f"{product.product_name} laptop"
                self.stdout.write(f'({i+1}/{total_products}) Searching for: "{search_term}"')
                
                search_url = f"https://duckduckgo.com/?q={search_term.replace(' ', '+')}&t=h_&iax=images&ia=images"
                driver.get(search_url)
                time.sleep(random.uniform(2.5, 4.5))

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                image_tag = soup.select_one('div[data-testid="zci-images"] img')

                if image_tag and image_tag.has_attr('src'):
                    image_url = image_tag['src']
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url

                    self.stdout.write(f'Downloading from: {image_url}')
                    
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    proxies = {"http": None, "https": None} # برای اطمینان از عدم وجود مشکل پراکسی
                    image_response = requests.get(image_url, headers=headers, proxies=proxies, timeout=15)
                    image_response.raise_for_status()
                    
                    # *** بخش کلیدی و اصلاح شده ***
                    # استفاده از فایل ذخیره‌سازی جنگو برای ذخیره صحیح در مسیر MEDIA_ROOT
                    image_filename = f"{product.slug}.jpg"
                    product.image_name.save(
                        image_filename,
                        ContentFile(image_response.content),
                        save=True # این دستور هم مدل را ذخیره می‌کند
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully saved image for "{product.product_name}"'))
                else:
                    self.stdout.write(self.style.WARNING(f'No image found for "{product.product_name}"'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred for product ID {product.id}: {e}'))
                continue
            
            if i < total_products - 1:
                wait_time = random.uniform(2.0, 5.0)
                self.stdout.write(f'Waiting for {wait_time:.2f} seconds...')
                time.sleep(wait_time)

        driver.quit()
        self.stdout.write(self.style.SUCCESS('Finished processing all products.'))