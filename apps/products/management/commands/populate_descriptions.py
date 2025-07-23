# FILE: apps/products/management/commands/populate_descriptions.py

import time
import random
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.products.models import Product

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

import os
from django.conf import settings

class Command(BaseCommand):
    help = 'A robust, Selenium-only scraper for product descriptions using DuckDuckGo.'
    MIN_CONTENT_LENGTH = 2000
    SEARCH_RESULTS_TO_CHECK = 4
    TRANSLATION_MAX_LENGTH = 4800

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Limits the number of products to process.', default=None)

    def handle(self, *args, **kwargs):
        limit = kwargs['limit']
        self.stdout.write(self.style.SUCCESS('▶️ Starting robust, Selenium-only scrape process...'))
        
        driver = self._setup_driver()
        if not driver: return

        products_to_update = Product.objects.filter(
            Q(description__in=['', None]) & Q(summery_description__in=['', None])
        ).order_by('?')

        if limit:
            products_to_update = products_to_update[:limit]
            self.stdout.write(self.style.HTTP_INFO(f'🧪 Running in test mode. Processing {limit} random products.'))

        total_products = products_to_update.count()
        if total_products == 0:
            self.stdout.write(self.style.SUCCESS('✅ All products already have descriptions.'))
            driver.quit()
            return
            
        self.stdout.write(f'🔍 Found {total_products} products to process.')
        self.stdout.write("="*50)

        for i, product in enumerate(products_to_update):
            self.stdout.write(self.style.HTTP_INFO(f'({i+1}/{total_products}) Processing: "{product.product_name}"'))
            
            search_term = f"review {product.product_name} specs"
            links = self.get_duckduckgo_search_links(driver, search_term)

            if not links:
                self.stdout.write(self.style.ERROR(f'  - ❌ Could not find any links for this product.'))
                self.stdout.write("-" * 50)
                continue

            content_found, _ = self.process_links(driver, links, product)

            if not content_found:
                self.stdout.write(self.style.ERROR(f'  - ❌ Could not find usable content from the found links.'))

            self.stdout.write("-" * 50)
            if i < total_products - 1:
                time.sleep(random.uniform(5.0, 8.0))

        driver.quit()
        self.stdout.write(self.style.SUCCESS('\n🏁 Finished processing all products.'))

    def process_links(self, driver, links, product):
        for link_url in links:
            self.stdout.write(f'  - Scraping link: {link_url[:70]}...')
            eng_content = self._scrape_content_from_url(driver, link_url)
            
            if eng_content and len(eng_content) > self.MIN_CONTENT_LENGTH:
                self.stdout.write(self.style.SUCCESS(f'  - ✅ Found high-quality English content ({len(eng_content)} chars).'))
                self.stdout.write('  - 🌐 Translating content to Persian...')
                try:
                    if len(eng_content) > self.TRANSLATION_MAX_LENGTH:
                        truncated_content = eng_content[:self.TRANSLATION_MAX_LENGTH]
                        last_period_index = truncated_content.rfind('.')
                        eng_content = truncated_content[:last_period_index + 1] if last_period_index != -1 else truncated_content

                    translator = GoogleTranslator(source='en', target='fa')
                    summary_en, full_desc_en = self._extract_summaries(eng_content)
                    summary_fa = translator.translate(summary_en)
                    full_desc_fa = translator.translate(full_desc_en)
                    
                    if not summary_fa or not full_desc_fa: raise Exception("Translation returned empty string.")

                    product.summery_description = summary_fa
                    product.description = full_desc_fa
                    product.save(update_fields=['summery_description', 'description'])
                    
                    self.stdout.write(self.style.SUCCESS(f'  - 💾 Persian description saved for "{product.product_name}"'))
                    return True, link_url
                except Exception as trans_err:
                    self.stdout.write(self.style.ERROR(f'  - ⛔ Translation failed: {trans_err}'))
                    continue
            else:
                self.stdout.write(self.style.WARNING(f'  - ⚠️ Content too short or not found. Trying next link...'))
        
        return False, None

    def _setup_driver(self):
        try:
            options = uc.ChromeOptions()
            # *** حالت Headless برای دیباگ غیرفعال شده است تا بتوانید مرورگر را ببینید ***
            # options.add_argument('--headless') 
            
            driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
            
            self.stdout.write("🚀 Setting up driver with manual path...")
            self.stdout.write(f"   - Driver path: {driver_path}")

            if not os.path.exists(driver_path):
                self.stdout.write(self.style.ERROR("⛔ chromedriver.exe not found at project root!"))
                self.stdout.write(self.style.WARNING("Please download the correct version and place it next to manage.py"))
                return None

            driver = uc.Chrome(options=options, driver_executable_path=driver_path)
            
            self.stdout.write(self.style.SUCCESS('✅ Driver started successfully in VISIBLE mode.'))
            return driver
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"⛔ Could not start driver. Error: {e}"))
            return None

    def get_duckduckgo_search_links(self, driver, query):
        """
        *** این تابع برای استفاده از XPath مقاوم‌سازی شده است ***
        """
        try:
            self.stdout.write("  - 🔎 Searching on DuckDuckGo...")
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
            driver.get(search_url)

            wait = WebDriverWait(driver, 10)
            
            # *** استفاده از XPath برای پیدا کردن لینک‌ها بر اساس ساختار صفحه ***
            # این عبارت به دنبال تگ <a> می‌گردد که داخل یک تگ <h2> باشد.
            xpath_selector = "//h2/a"
            
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
            self.stdout.write(self.style.SUCCESS(f"  - Successfully found search results using XPath: '{xpath_selector}'"))
            
            link_tags = driver.find_elements(By.XPATH, xpath_selector)
            
            links = [tag.get_attribute('href') for tag in link_tags if tag.get_attribute('href')]
            
            return list(dict.fromkeys(links))[:self.SEARCH_RESULTS_TO_CHECK]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  - ⛔ Error during DuckDuckGo search: {e}'))
            return []

    def _scrape_content_from_url(self, driver, url):
        try:
            driver.get(url)
            time.sleep(random.uniform(2.5, 4.5))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
                tag.decompose()
            content_area = None
            selectors = ['article', 'main', '.post-content', '.entry-content', '#product-description', '#content', 'div[role="main"]']
            for selector in selectors:
                content_area = soup.select_one(selector)
                if content_area: break
            if not content_area: content_area = soup.body
            JUNK_KEYWORDS = ['customer', 'review', 'rating', 'stars', 'comment', 'helpful', 'report', 'compare', 'price', 'buy now', 'add to cart', 'related products', 'faq', 'q&a', 'specification', 'read more', 'find helpful', 'verified purchase', 'out of 5 stars']
            MIN_PARAGRAPH_WORDS = 10
            all_paragraphs = content_area.find_all('p')
            clean_text_parts = []
            for p in all_paragraphs:
                p_text = p.get_text(strip=True)
                if len(p_text.split()) < MIN_PARAGRAPH_WORDS: continue
                if any(junk in p_text.lower() for junk in JUNK_KEYWORDS): continue
                clean_text_parts.append(p_text)
            return "\n\n".join(clean_text_parts)
        except Exception:
            return ""

    def _extract_summaries(self, text):
        lines = [line for line in text.split('\n') if line.strip()]
        summary = lines[0] if lines else ""
        return summary, "\n".join(lines)


# # # FILE: apps/products/management/commands/populate_descriptions.py

# # import time
# # import random
# # from django.core.management.base import BaseCommand
# # from django.db.models import Q
# # from apps.products.models import Product

# # import undetected_chromedriver as uc
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from bs4 import BeautifulSoup
# # from deep_translator import GoogleTranslator

# # import os
# # from django.conf import settings

# # class Command(BaseCommand):
# #     help = 'A robust, Selenium-only scraper that prioritizes the longest content.'
# #     MIN_CONTENT_LENGTH = 150
# #     SEARCH_RESULTS_TO_CHECK = 3
# #     TRANSLATION_MAX_LENGTH = 4500

# #     def add_arguments(self, parser):
# #         parser.add_argument('--limit', type=int, help='Limits the number of products to process.', default=None)

# #     def handle(self, *args, **kwargs):
# #         limit = kwargs['limit']
# #         self.stdout.write(self.style.SUCCESS('▶️ Starting robust, Selenium-only scrape process...'))
        
# #         driver = self._setup_driver()
# #         if not driver: return

# #         products_to_update = Product.objects.filter(
# #             Q(description__in=['', None]) & Q(summery_description__in=['', None])
# #         ).order_by('?')

# #         if limit:
# #             products_to_update = products_to_update[:limit]
# #             self.stdout.write(self.style.HTTP_INFO(f'🧪 Running in test mode. Processing {limit} random products.'))

# #         total_products = products_to_update.count()
# #         if total_products == 0:
# #             self.stdout.write(self.style.SUCCESS('✅ All products already have descriptions.'))
# #             driver.quit()
# #             return
            
# #         self.stdout.write(f'🔍 Found {total_products} products to process.')
# #         self.stdout.write("="*50)

# #         for i, product in enumerate(products_to_update):
# #             self.stdout.write(self.style.HTTP_INFO(f'({i+1}/{total_products}) Processing: "{product.product_name}"'))
            
# #             search_term = f"review {product.product_name} specs"
# #             links = self.get_duckduckgo_search_links(driver, search_term)

# #             if not links:
# #                 self.stdout.write(self.style.ERROR(f'  - ❌ Could not find any links for this product.'))
# #                 self.stdout.write("-" * 50)
# #                 continue

# #             # تابع process_links اکنون بهترین لینک را انتخاب و پردازش می‌کند
# #             content_found, _ = self.process_links(driver, links, product)

# #             if not content_found:
# #                 self.stdout.write(self.style.ERROR(f'  - ❌ Could not find usable content from the found links.'))

# #             self.stdout.write("-" * 50)
# #             if i < total_products - 1:
# #                 time.sleep(random.uniform(5.0, 8.0))

# #         driver.quit()
# #         self.stdout.write(self.style.SUCCESS('\n🏁 Finished processing all products.'))

# #     def process_links(self, driver, links, product):
# #         """
# #         *** جدید: این تابع بازنویسی شده تا همه لینک‌ها را بررسی و بهترین را انتخاب کند ***
# #         """
# #         potential_results = []
# #         # مرحله ۱: تمام لینک‌ها را بررسی و محتوای آنها را استخراج کن
# #         for link_url in links:
# #             self.stdout.write(f'  - Evaluating link: {link_url[:70]}...')
# #             eng_content = self._scrape_content_from_url(driver, link_url)
            
# #             if eng_content and len(eng_content) > self.MIN_CONTENT_LENGTH:
# #                 # محتوای معتبر را به همراه طول آن ذخیره کن
# #                 potential_results.append((len(eng_content), eng_content, link_url))
# #                 self.stdout.write(f"    - Found valid content with length: {len(eng_content)}")
# #             else:
# #                 self.stdout.write(self.style.WARNING(f'    - Content too short or not found.'))

# #         # مرحله ۲: اگر هیچ محتوای معتبری پیدا نشد، کار را متوقف کن
# #         if not potential_results:
# #             return False, None

# #         # مرحله ۳: نتایج را بر اساس طول محتوا مرتب کرده و بهترین را انتخاب کن
# #         potential_results.sort(key=lambda x: x[0], reverse=True)
# #         best_content_len, best_content, best_url = potential_results[0]
# #         self.stdout.write(self.style.SUCCESS(f'  - ✅ Selected best link with {best_content_len} chars: {best_url[:70]}...'))
        
# #         # مرحله ۴: بهترین محتوا را ترجمه و ذخیره کن
# #         self.stdout.write('  - 🌐 Translating best content to Persian...')
# #         try:
# #             if len(best_content) > self.TRANSLATION_MAX_LENGTH:
# #                 truncated_content = best_content[:self.TRANSLATION_MAX_LENGTH]
# #                 last_period_index = truncated_content.rfind('.')
# #                 best_content = truncated_content[:last_period_index + 1] if last_period_index != -1 else truncated_content

# #             translator = GoogleTranslator(source='en', target='fa')
# #             summary_en, full_desc_en = self._extract_summaries(best_content)
# #             summary_fa = translator.translate(summary_en)
# #             full_desc_fa = translator.translate(full_desc_en) # چون متن کوتاه شده، دیگر نیازی به chunking نیست
            
# #             if not summary_fa or not full_desc_fa: raise Exception("Translation returned empty string.")

# #             product.summery_description = summary_fa
# #             product.description = full_desc_fa
# #             product.save(update_fields=['summery_description', 'description'])
            
# #             self.stdout.write(self.style.SUCCESS(f'  - 💾 Persian description saved for "{product.product_name}"'))
# #             return True, best_url
# #         except Exception as trans_err:
# #             self.stdout.write(self.style.ERROR(f'  - ⛔ Translation failed for the best content: {trans_err}'))
# #             return False, None

# #     def _setup_driver(self):
# #         try:
# #             options = uc.ChromeOptions()
# #             # options.add_argument('--headless') 
            
# #             driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
            
# #             self.stdout.write("🚀 Setting up driver with manual path...")
# #             self.stdout.write(f"  - Driver path: {driver_path}")

# #             if not os.path.exists(driver_path):
# #                 self.stdout.write(self.style.ERROR("⛔ chromedriver.exe not found at project root!"))
# #                 return None

# #             driver = uc.Chrome(options=options, driver_executable_path=driver_path)
            
# #             self.stdout.write(self.style.SUCCESS('✅ Driver started successfully in VISIBLE mode.'))
# #             return driver
# #         except Exception as e:
# #             self.stdout.write(self.style.ERROR(f"⛔ Could not start driver. Error: {e}"))
# #             return None

# #     def get_duckduckgo_search_links(self, driver, query):
# #         try:
# #             self.stdout.write("  - 🔎 Searching on DuckDuckGo...")
# #             search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
# #             driver.get(search_url)
# #             wait = WebDriverWait(driver, 10)
# #             xpath_selector = "//h2/a"
# #             wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
# #             self.stdout.write(self.style.SUCCESS(f"  - Successfully found search results using XPath: '{xpath_selector}'"))
# #             link_tags = driver.find_elements(By.XPATH, xpath_selector)
# #             links = [tag.get_attribute('href') for tag in link_tags if tag.get_attribute('href')]
# #             return list(dict.fromkeys(links))[:self.SEARCH_RESULTS_TO_CHECK]
# #         except Exception as e:
# #             self.stdout.write(self.style.ERROR(f'  - ⛔ Error during DuckDuckGo search: {e}'))
# #             return []

# #     def _scrape_content_from_url(self, driver, url):
# #         try:
# #             driver.get(url)
# #             time.sleep(random.uniform(2.5, 4.5))
# #             soup = BeautifulSoup(driver.page_source, 'html.parser')
# #             for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
# #                 tag.decompose()
# #             content_area = None
# #             selectors = ['article', 'main', '.post-content', '.entry-content', '#product-description', '#content', 'div[role="main"]']
# #             for selector in selectors:
# #                 content_area = soup.select_one(selector)
# #                 if content_area: break
# #             if not content_area: content_area = soup.body
# #             JUNK_KEYWORDS = ['customer', 'review', 'rating', 'stars', 'comment', 'helpful', 'report', 'compare', 'price', 'buy now', 'add to cart', 'related products', 'faq', 'q&a', 'specification', 'read more', 'find helpful', 'verified purchase', 'out of 5 stars']
# #             MIN_PARAGRAPH_WORDS = 10
# #             all_paragraphs = content_area.find_all('p')
# #             clean_text_parts = []
# #             for p in all_paragraphs:
# #                 p_text = p.get_text(strip=True)
# #                 if len(p_text.split()) < MIN_PARAGRAPH_WORDS: continue
# #                 if any(junk in p_text.lower() for junk in JUNK_KEYWORDS): continue
# #                 clean_text_parts.append(p_text)
# #             return "\n\n".join(clean_text_parts)
# #         except Exception:
# #             return ""

# #     def _extract_summaries(self, text):
# #         lines = [line for line in text.split('\n') if line.strip()]
# #         summary = lines[0] if lines else ""
# #         return summary, "\n".join(lines)










# # -------------------------------------------------

# # FILE: apps/products/management/commands/populate_descriptions.py

# import time
# import random
# import csv  # جدید: ماژول csv برای کار با فایل‌های CSV اضافه شد
# import os
# from django.core.management.base import BaseCommand
# from django.db.models import Q
# from apps.products.models import Product
# from django.conf import settings

# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# from deep_translator import GoogleTranslator

# class Command(BaseCommand):
#     help = 'A robust scraper for product descriptions that saves results to a CSV file.'
#     MIN_CONTENT_LENGTH = 150
#     SEARCH_RESULTS_TO_CHECK = 3
#     TRANSLATION_MAX_LENGTH = 4500

#     def add_arguments(self, parser):
#         parser.add_argument('--limit', type=int, help='Limits the number of products to process.', default=None)
#         # جدید: آرگومانی برای تعیین نام فایل خروجی CSV
#         parser.add_argument(
#             '--output', 
#             type=str, 
#             help='The name of the output CSV file.', 
#             default='product_descriptions.csv'
#         )

#     def handle(self, *args, **kwargs):
#         limit = kwargs['limit']
#         output_filename = kwargs['output'] # جدید: دریافت نام فایل خروجی از آرگومان‌ها
        
#         self.stdout.write(self.style.SUCCESS('▶️ Starting scrape process to generate CSV...'))
        
#         driver = self._setup_driver()
#         if not driver: return

#         products_to_process = Product.objects.filter(
#             Q(description__in=['', None]) & Q(summery_description__in=['', None])
#         ).order_by('?')

#         if limit:
#             products_to_process = products_to_process[:limit]
#             self.stdout.write(self.style.HTTP_INFO(f'🧪 Running in test mode. Processing {limit} random products.'))

#         total_products = products_to_process.count()
#         if total_products == 0:
#             self.stdout.write(self.style.SUCCESS('✅ All products already have descriptions.'))
#             driver.quit()
#             return
            
#         self.stdout.write(f'🔍 Found {total_products} products to process.')
#         self.stdout.write(f"💾 Results will be saved to: {output_filename}")
#         self.stdout.write("="*50)

#         # جدید: باز کردن فایل CSV برای نوشتن اطلاعات
#         # از 'utf-8-sig' برای سازگاری بهتر با اکسل و کاراکترهای فارسی استفاده می‌کنیم
#         try:
#             with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
#                 # جدید: تعریف ستون‌های فایل CSV
#                 fieldnames = ['product_id', 'product_name', 'description', 'short_description']
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writeheader() # جدید: نوشتن هدر (سرستون‌ها) در فایل

#                 for i, product in enumerate(products_to_process):
#                     self.stdout.write(self.style.HTTP_INFO(f'({i+1}/{total_products}) Processing: "{product.product_name}"'))
                    
#                     search_term = f"review {product.product_name} specs"
#                     links = self.get_duckduckgo_search_links(driver, search_term)

#                     if not links:
#                         self.stdout.write(self.style.ERROR(f'  - ❌ Could not find any links for this product.'))
#                         self.stdout.write("-" * 50)
#                         continue

#                     # جدید: تابع process_links حالا توضیحات را برمی‌گرداند
#                     full_desc_fa, summary_fa = self.process_links(driver, links)

#                     if full_desc_fa and summary_fa:
#                         # جدید: نوشتن اطلاعات در یک ردیف از فایل CSV
#                         writer.writerow({
#                             'product_id': product.id,
#                             'product_name': product.product_name,
#                             'description': full_desc_fa,
#                             'short_description': summary_fa
#                         })
#                         self.stdout.write(self.style.SUCCESS(f'  - ✅ Successfully wrote "{product.product_name}" to CSV.'))
#                     else:
#                         self.stdout.write(self.style.ERROR(f'  - ❌ Could not find usable content for this product.'))

#                     self.stdout.write("-" * 50)
#                     if i < total_products - 1:
#                         time.sleep(random.uniform(5.0, 8.0))

#         except IOError as e:
#             self.stdout.write(self.style.ERROR(f"⛔ Error writing to file {output_filename}: {e}"))
#         finally:
#             driver.quit()
#             self.stdout.write(self.style.SUCCESS(f'\n🏁 Finished processing. Data saved in {output_filename}.'))


#     def process_links(self, driver, links): # جدید: پارامتر product حذف شد چون دیگر به آن نیازی نیست
#         """
#         این تابع بهترین لینک را پیدا کرده و محتوای ترجمه‌شده را برمی‌گرداند.
#         """
#         potential_results = []
#         for link_url in links:
#             self.stdout.write(f'  - Evaluating link: {link_url[:70]}...')
#             eng_content = self._scrape_content_from_url(driver, link_url)
            
#             if eng_content and len(eng_content) > self.MIN_CONTENT_LENGTH:
#                 potential_results.append((len(eng_content), eng_content))
#                 self.stdout.write(f"    - Found valid content with length: {len(eng_content)}")
#             else:
#                 self.stdout.write(self.style.WARNING(f'    - Content too short or not found.'))

#         if not potential_results:
#             return None, None # جدید: در صورت عدم موفقیت، None برمی‌گرداند

#         potential_results.sort(key=lambda x: x[0], reverse=True)
#         _, best_content = potential_results[0]
        
#         self.stdout.write('  - 🌐 Translating best content to Persian...')
#         try:
#             if len(best_content) > self.TRANSLATION_MAX_LENGTH:
#                 truncated_content = best_content[:self.TRANSLATION_MAX_LENGTH]
#                 last_period_index = truncated_content.rfind('.')
#                 best_content = truncated_content[:last_period_index + 1] if last_period_index != -1 else truncated_content

#             translator = GoogleTranslator(source='en', target='fa')
#             summary_en, full_desc_en = self._extract_summaries(best_content)
#             summary_fa = translator.translate(summary_en)
#             full_desc_fa = translator.translate(full_desc_en)
            
#             if not summary_fa or not full_desc_fa: raise Exception("Translation returned empty string.")
            
#             # جدید: به جای ذخیره در دیتابیس، مقادیر ترجمه‌شده را برمی‌گردانیم
#             return full_desc_fa, summary_fa
            
#         except Exception as trans_err:
#             self.stdout.write(self.style.ERROR(f'  - ⛔ Translation failed for the best content: {trans_err}'))
#             return None, None # جدید: در صورت خطا در ترجمه، None برمی‌گرداند

#     # توابع کمکی دیگر بدون تغییر باقی می‌مانند
#     def _setup_driver(self):
#         try:
#             options = uc.ChromeOptions()
#             # options.add_argument('--headless') 
#             driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
#             if not os.path.exists(driver_path):
#                 self.stdout.write(self.style.ERROR("⛔ chromedriver.exe not found!"))
#                 return None
#             driver = uc.Chrome(options=options, driver_executable_path=driver_path)
#             self.stdout.write(self.style.SUCCESS('✅ Driver started successfully.'))
#             return driver
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"⛔ Could not start driver. Error: {e}"))
#             return None

#     def get_duckduckgo_search_links(self, driver, query):
#         try:
#             self.stdout.write("  - 🔎 Searching on DuckDuckGo...")
#             search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
#             driver.get(search_url)
#             wait = WebDriverWait(driver, 10)
#             xpath_selector = "//h2/a"
#             wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
#             link_tags = driver.find_elements(By.XPATH, xpath_selector)
#             links = [tag.get_attribute('href') for tag in link_tags if tag.get_attribute('href')]
#             return list(dict.fromkeys(links))[:self.SEARCH_RESULTS_TO_CHECK]
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'  - ⛔ Error during DuckDuckGo search: {e}'))
#             return []

#     def _scrape_content_from_url(self, driver, url):
#         try:
#             driver.get(url)
#             time.sleep(random.uniform(2.5, 4.5))
#             soup = BeautifulSoup(driver.page_source, 'html.parser')
#             for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
#                 tag.decompose()
#             content_area = None
#             selectors = ['article', 'main', '.post-content', '.entry-content', '#product-description', '#content', 'div[role="main"]']
#             for selector in selectors:
#                 content_area = soup.select_one(selector)
#                 if content_area: break
#             if not content_area: content_area = soup.body
#             JUNK_KEYWORDS = ['customer', 'review', 'rating', 'stars', 'comment', 'helpful', 'report', 'compare', 'price', 'buy now', 'add to cart', 'related products', 'faq', 'q&a', 'specification', 'read more', 'find helpful', 'verified purchase', 'out of 5 stars']
#             MIN_PARAGRAPH_WORDS = 10
#             all_paragraphs = content_area.find_all('p')
#             clean_text_parts = []
#             for p in all_paragraphs:
#                 p_text = p.get_text(strip=True)
#                 if len(p_text.split()) < MIN_PARAGRAPH_WORDS: continue
#                 if any(junk in p_text.lower() for junk in JUNK_KEYWORDS): continue
#                 clean_text_parts.append(p_text)
#             return "\n\n".join(clean_text_parts)
#         except Exception:
#             return ""

#     def _extract_summaries(self, text):
#         lines = [line for line in text.split('\n') if line.strip()]
#         summary = lines[0] if lines else ""
#         return summary, "\n".join(lines)