
import requests
import time
from django.core.management.base import BaseCommand
from apps.products.models import Product  # مسیر مدل محصول شما
from django.conf import settings

# آدرس API و مدل مورد استفاده در Hugging Face
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
MODEL_NAME = "Mixtral-8x7B"

class Command(BaseCommand):
    help = 'Formats a single product description using the free Hugging Face API for testing.'

    def handle(self, *args, **kwargs):
        # =================================================================
        # مرحله ۱: شناسه (ID) محصولی که می‌خواهید تست کنید را اینجا وارد کنید
        # =================================================================
        TEST_PRODUCT_ID = 905  # <--- ID محصول مورد نظر خود را جایگزین کنید
        # =================================================================

        try:
            # توکن را مستقیماً از settings.py یا اینجا قرار دهید
            token = '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'
        except AttributeError:
            self.stdout.write(self.style.ERROR('HUGGING_FACE_TOKEN not found in settings.py.'))
            return

        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            product = Product.objects.get(id=TEST_PRODUCT_ID)
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Product with ID {TEST_PRODUCT_ID} not found.'))
            return

        self.stdout.write(f'Processing product for test: "{product.product_name}" (ID: {product.id})')

        if not product.description:
            self.stdout.write(self.style.ERROR('Product description is empty. Cannot test.'))
            return

        prompt = f"""
        You are an expert web content designer specializing in formatting product pages for an e-commerce website that sells laptops.
        Your task is to convert the following plain-text Persian laptop description into a beautifully formatted, engaging, and professional HTML snippet.

        **Formatting Rules (Strictly Follow):**

        1.  **Main Container:** Enclose the entire output in a single `<div>` tag with RTL direction and justified text alignment. Like this: `<div style="direction: rtl; text-align: justify;"> ... </div>`.
        2.  **Headings:** Identify logical sections and introduce them with clear, concise headings. Use `<h3>` for main sections and `<h4>` for sub-sections.
        3.  **Paragraphs:** Break the text into logical paragraphs using `<p>` tags. Ensure proper spacing between paragraphs for readability.
        4.  **Emphasis:**
            * Use `<strong>` to bold important keywords. Keywords include the brand (ASUS, etc.), model name (Vivobook, etc.), technical specifications (OLED, Core i9, 16GB RAM), and special features (Trackpad, etc.).
            * Use `<u>` (underline) ONLY for the main title or a very specific phrase that needs special attention. Do not overuse it.
        5.  **Content Integrity:**
            * The final output **must be in Persian**.
            * Do **not** add any new information or invent facts.
            * Do **not** shorten the original text, but you are allowed to remove parts that are clearly irrelevant, repetitive, or nonsensical to improve quality.

        **Output Format:**
        The output must be **ONLY the raw HTML code**, starting with the main `<div>` tag and containing the formatted Persian text.

        **Plain text to format:**
        ---
        {product.description}
        ---
        """

        try:
            # قبل از اجرای اسکریپت، مدل را در صفحه Hugging Face بیدار کنید
            self.stdout.write("Sending request to Hugging Face... (This may take a moment if the model is loading)")
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=90)

            if response.status_code == 200:
                result_text = response.json()[0]['generated_text']
                # استخراج کد HTML از پاسخ مدل
                html_output = result_text.split('---')[-1].strip()
                
                self.stdout.write(self.style.SUCCESS('--- HTML Output ---'))
                self.stdout.write(html_output)
                self.stdout.write(self.style.SUCCESS('--- End of Output ---'))
                
                # برای ذخیره در دیتابیس، این سه خط را از کامنت خارج کنید
                # product.description = html_output
                # product.save()
                # self.stdout.write(self.style.SUCCESS(f'Product ID {product.id} has been saved to the database.'))
                
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.status_code} - {response.text}'))

        except requests.exceptions.Timeout:
             self.stdout.write(self.style.ERROR('The request timed out. The model might still be loading. Please try running the script again in a minute.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))