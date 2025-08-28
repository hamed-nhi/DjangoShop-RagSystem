# FILE: apps/products/management/commands/populate_descriptions.py
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
    MIN_CONTENT_LENGTH = 1500
    SEARCH_RESULTS_TO_CHECK = 5
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
                self.stdout.write(self.style.ERROR(f'   - ❌ Could not find any links for this product.'))
                self.stdout.write("-" * 50)
                continue

            content_found, _ = self.process_links(driver, links, product)

            if not content_found:
                self.stdout.write(self.style.ERROR(f'   - ❌ Could not find usable content from the found links.'))

            self.stdout.write("-" * 50)
            if i < total_products - 1:
                time.sleep(random.uniform(5.0, 8.0))

        driver.quit()
        self.stdout.write(self.style.SUCCESS('\n🏁 Finished processing all products.'))

    def process_links(self, driver, links, product):
        for link_url in links:
            self.stdout.write(f'   - Scraping link: {link_url[:70]}...')
            eng_content = self._scrape_content_from_url(driver, link_url)
            
            if eng_content and len(eng_content) > self.MIN_CONTENT_LENGTH:
                self.stdout.write(self.style.SUCCESS(f'   - ✅ Found high-quality English content ({len(eng_content)} chars).'))
                self.stdout.write('   - 🌐 Translating content to Persian...')
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
                    # 👇 تغییر اعمال شده در اینجا
                    product.save() 
                    
                    self.stdout.write(self.style.SUCCESS(f'   - 💾 Persian description saved for "{product.product_name}"'))
                    return True, link_url
                except Exception as trans_err:
                    self.stdout.write(self.style.ERROR(f'   - ⛔ Translation failed: {trans_err}'))
                    continue
            else:
                self.stdout.write(self.style.WARNING(f'   - ⚠️ Content too short or not found. Trying next link...'))
        
        return False, None

    def _setup_driver(self):
        try:
            options = uc.ChromeOptions()
            # *** حالت Headless برای دیباگ غیرفعال شده است تا بتوانید مرورگر را ببینید ***
            # options.add_argument('--headless') 
            
            driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
            
            self.stdout.write("🚀 Setting up driver with manual path...")
            self.stdout.write(f"    - Driver path: {driver_path}")

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
            self.stdout.write("   - 🔎 Searching on DuckDuckGo...")
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
            driver.get(search_url)

            wait = WebDriverWait(driver, 10)
            
            # *** استفاده از XPath برای پیدا کردن لینک‌ها بر اساس ساختار صفحه ***
            # این عبارت به دنبال تگ <a> می‌گردد که داخل یک تگ <h2> باشد.
            xpath_selector = "//h2/a"
            
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
            self.stdout.write(self.style.SUCCESS(f"   - Successfully found search results using XPath: '{xpath_selector}'"))
            
            link_tags = driver.find_elements(By.XPATH, xpath_selector)
            
            links = [tag.get_attribute('href') for tag in link_tags if tag.get_attribute('href')]
            
            return list(dict.fromkeys(links))[:self.SEARCH_RESULTS_TO_CHECK]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   - ⛔ Error during DuckDuckGo search: {e}'))
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
# import time
# import random
# from django.core.management.base import BaseCommand
# from django.db.models import Q
# from apps.products.models import Product

# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# from deep_translator import GoogleTranslator

# import os
# from django.conf import settings

# class Command(BaseCommand):
#     help = 'A robust, Selenium-only scraper for product descriptions using DuckDuckGo.'
#     MIN_CONTENT_LENGTH = 2000
#     SEARCH_RESULTS_TO_CHECK = 7
#     TRANSLATION_MAX_LENGTH = 4800

#     def add_arguments(self, parser):
#         parser.add_argument('--limit', type=int, help='Limits the number of products to process.', default=None)

#     def handle(self, *args, **kwargs):
#         limit = kwargs['limit']
#         self.stdout.write(self.style.SUCCESS('▶️ Starting robust, Selenium-only scrape process...'))
        
#         driver = self._setup_driver()
#         if not driver: return

#         products_to_update = Product.objects.filter(
#             Q(description__in=['', None]) & Q(summery_description__in=['', None])
#         ).order_by('?')

#         if limit:
#             products_to_update = products_to_update[:limit]
#             self.stdout.write(self.style.HTTP_INFO(f'🧪 Running in test mode. Processing {limit} random products.'))

#         total_products = products_to_update.count()
#         if total_products == 0:
#             self.stdout.write(self.style.SUCCESS('✅ All products already have descriptions.'))
#             driver.quit()
#             return
            
#         self.stdout.write(f'🔍 Found {total_products} products to process.')
#         self.stdout.write("="*50)

#         for i, product in enumerate(products_to_update):
#             self.stdout.write(self.style.HTTP_INFO(f'({i+1}/{total_products}) Processing: "{product.product_name}"'))
            
#             search_term = f"review {product.product_name} specs"
#             links = self.get_duckduckgo_search_links(driver, search_term)

#             if not links:
#                 self.stdout.write(self.style.ERROR(f'  - ❌ Could not find any links for this product.'))
#                 self.stdout.write("-" * 50)
#                 continue

#             content_found, _ = self.process_links(driver, links, product)

#             if not content_found:
#                 self.stdout.write(self.style.ERROR(f'  - ❌ Could not find usable content from the found links.'))

#             self.stdout.write("-" * 50)
#             if i < total_products - 1:
#                 time.sleep(random.uniform(5.0, 8.0))

#         driver.quit()
#         self.stdout.write(self.style.SUCCESS('\n🏁 Finished processing all products.'))

#     def process_links(self, driver, links, product):
#         for link_url in links:
#             self.stdout.write(f'  - Scraping link: {link_url[:70]}...')
#             eng_content = self._scrape_content_from_url(driver, link_url)
            
#             if eng_content and len(eng_content) > self.MIN_CONTENT_LENGTH:
#                 self.stdout.write(self.style.SUCCESS(f'  - ✅ Found high-quality English content ({len(eng_content)} chars).'))
#                 self.stdout.write('  - 🌐 Translating content to Persian...')
#                 try:
#                     if len(eng_content) > self.TRANSLATION_MAX_LENGTH:
#                         truncated_content = eng_content[:self.TRANSLATION_MAX_LENGTH]
#                         last_period_index = truncated_content.rfind('.')
#                         eng_content = truncated_content[:last_period_index + 1] if last_period_index != -1 else truncated_content

#                     translator = GoogleTranslator(source='en', target='fa')
#                     summary_en, full_desc_en = self._extract_summaries(eng_content)
#                     summary_fa = translator.translate(summary_en)
#                     full_desc_fa = translator.translate(full_desc_en)
                    
#                     if not summary_fa or not full_desc_fa: raise Exception("Translation returned empty string.")

#                     product.summery_description = summary_fa
#                     product.description = full_desc_fa
#                     product.save(update_fields=['summery_description', 'description'])
                    
#                     self.stdout.write(self.style.SUCCESS(f'  - 💾 Persian description saved for "{product.product_name}"'))
#                     return True, link_url
#                 except Exception as trans_err:
#                     self.stdout.write(self.style.ERROR(f'  - ⛔ Translation failed: {trans_err}'))
#                     continue
#             else:
#                 self.stdout.write(self.style.WARNING(f'  - ⚠️ Content too short or not found. Trying next link...'))
        
#         return False, None

#     def _setup_driver(self):
#         try:
#             options = uc.ChromeOptions()
#             # *** حالت Headless برای دیباگ غیرفعال شده است تا بتوانید مرورگر را ببینید ***
#             # options.add_argument('--headless') 
            
#             driver_path = os.path.join(settings.BASE_DIR, 'chromedriver.exe')
            
#             self.stdout.write("🚀 Setting up driver with manual path...")
#             self.stdout.write(f"   - Driver path: {driver_path}")

#             if not os.path.exists(driver_path):
#                 self.stdout.write(self.style.ERROR("⛔ chromedriver.exe not found at project root!"))
#                 self.stdout.write(self.style.WARNING("Please download the correct version and place it next to manage.py"))
#                 return None

#             driver = uc.Chrome(options=options, driver_executable_path=driver_path)
            
#             self.stdout.write(self.style.SUCCESS('✅ Driver started successfully in VISIBLE mode.'))
#             return driver
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"⛔ Could not start driver. Error: {e}"))
#             return None

#     def get_duckduckgo_search_links(self, driver, query):
#         """
#         *** این تابع برای استفاده از XPath مقاوم‌سازی شده است ***
#         """
#         try:
#             self.stdout.write("  - 🔎 Searching on DuckDuckGo...")
#             search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
#             driver.get(search_url)

#             wait = WebDriverWait(driver, 10)
            
#             # *** استفاده از XPath برای پیدا کردن لینک‌ها بر اساس ساختار صفحه ***
#             # این عبارت به دنبال تگ <a> می‌گردد که داخل یک تگ <h2> باشد.
#             xpath_selector = "//h2/a"
            
#             wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
#             self.stdout.write(self.style.SUCCESS(f"  - Successfully found search results using XPath: '{xpath_selector}'"))
            
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

