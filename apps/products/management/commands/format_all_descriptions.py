# myapp/management/commands/format_all_descriptions.py
import re
import hazm
import csv # Even if not writing to CSV, csv module might be useful for parsing if input data is CSV-like.
from django.core.management.base import BaseCommand
from django.utils.html import escape, mark_safe # These need to be imported here if they are not in Django's global context for commands.
from myapp.models import Product # Adjust 'myapp' to your actual app name

# --- Hazm Component Initialization (Load once for efficiency) ---
# IMPORTANT: When running a management command, this code runs once.
# If models are not found, it will print an error and exit.
try:
    normalizer = hazm.Normalizer()
    pos_tagger = hazm.POSTagger()
    ner = hazm.NamedEntityRecognizer()
    print("Hazm models loaded successfully.")
except Exception as e:
    print(f"Error loading Hazm models: {e}. Please ensure models are downloaded and paths are correct.")
    print("You can download them using: import hazm; hazm.utils.download_model('all')")
    exit(1) # Exit with an error code if critical components fail to load.


# --- Define Global Rule Sets (Lists of keywords and patterns) ---
# These lists are now directly within this file's scope.
HEADING_KEYWORDS = [
    "توضیحات کامل محصول", "مشخصات فنی", "ویژگی‌های اصلی", "جمع‌بندی", 
    "نتیجه‌گیری", "نقاط قوت", "نقاط ضعف", "مقدمه", "معرفی", "بررسی",
    "طراحی", "اتصالات", "صفحه نمایش", "صدا", "صفحه کلید", "تاچ پد",
    "عمر باتری", "عملکرد", "بنادر", "ذخیره و حافظه", "وب کم", "خنک کننده",
    "ملاحظات", "نکات مهم", "در قلب", "کیفیت ساخت"
]

BRANDS = [
    r'\bHP\b', r'\bDell\b', r'\bMSI\b', r'\bAsus\b', r'\bAcer\b', r'\bLenovo\b',
    r'\bApple\b', r'\bIntel\b', r'\bAMD\b', r'\bNVIDIA\b', r'\bQualcomm\b',
    r'\bZebronics\b', r'\bMicrosoft\b', r'\bSamsung\b', r'\bChuwi\b', r'\bInfinix\b',
    r'\bLG\b', r'\bWings\b', r'\biBall\b'
]

PRODUCT_NAME_COMPONENTS = [
    r'VivoBook', r'Zenbook', r'ROG Strix', r'TUF Gaming', r'IdeaPad', r'Chromebook',
    r'Victus', r'Omen', r'Spectre x360', r'ZBook Firefly', r'Inspiron', r'Vostro',
    r'MacBook Air', r'MacBook Pro', r'Predator Helios', r'Thin GF63', r'Sword 15',
    r'Bravo 15', r'LOQ 15', r'UltraPC', r'Nuvobook', r'Excelance CompBook', r'Summit E13 Flip Evo',
    r'Modern 14', r'Legion', r'Yoga', r'Flow X13', r'Alienware'
]

TECH_SPECS_PATTERNS = [
    r'\b\d+(\.\d+)?\s*(GB|TB|GHz|MHz|Watt|W|اینچ|پوند|کیلوگرم|میلی\s*متر|نیت|FPS|Hz|دسی\s*بل|EU|W|nm|p|\%)',
    r'\b(FHD|QHD|2\.8K|4K|OLED|IPS|LCD|TN)\b',
    r'\b(RTX|GTX|Iris\s*XE|UHD Graphics|Radeon\s*Vega|Quadro)\s*\d+[A-Z]*\b',
    r'\b(Core\s*i[3579]|Ryzen\s*[3579]|Apple\s*M[123]|Celeron|Athlon)\b',
    r'\b\d{1,2}(th\s*Gen|th\s*ژن)\b',
    r'\b(SSD|HDD|eMMC|RAM|DDR\d+|PCIE|NVME|DisplayPort|HDMI|USB(-[AC])?|Thunderbolt|Ethernet|Wi-Fi|Bluetooth|SD\s*Card|MagSafe)\b',
    r'\b(Windows\s*\d+|Chrome\s*OS|macOS|FreeDOS)\b',
    r'\b\d+(\.\d+)?\s*(x|×)\s*\d+(\.\d+)?\s*پیکسل\b',
    r'\b\d+\s*:\s*\d+\b'
]

SOFTWARE_GAMES = [
    r'Cyberpunk 2077', r'Fortnite', r'Far Cry 6', r'Borderlands 3', r'Grand Theft Auto V',
    r'Assassin\'s Creed Valhalla', r'Metro Exodus', r'Overwatch 2', r'Dirt 5', r'Hitman 3',
    r'Total War: Warhammer III', r'Lightroom', r'Photoshop', r'Microsoft Office', r'Windows',
    r'Chrome OS', r'macOS', r'Spotify', r'Canva', r'Premiere Pro', r'Steam', r'YouTube',
    r'Google Chrome', r'Zoom', r'Skype', r'McAfee', r'DTS', r'Dolby Atmos', 'Dolby Vision',
    r'Waves Maxxaudio Pro', r'Handbrake', r'Cinebench', r'PCMark', r'Geekbench', r'3DMark',
    r'Spinergy', r'Aura Sync', r'Armoury Crate', r'MyASUS', r'Dragon Center', r'Vantage',
    r'AI-Noise Cancellation', r'Whiskey Lake', r'Ice Lake', 'Alder Lake', 'Tiger Lake',
    'Raptor Lake', 'Rembrandt', 'Phoenix', 'Zen 2', 'Zen 3', 'Zen 4', 'Meteor Lake'
]

PROS_KEYWORDS = ["نقاط قوت", "مزایا", "برتری", "مثبت"]
CONS_KEYWORDS = ["نقاط ضعف", "معایب", "نکات منفی", "مشکلات", "اشکال", "ایراد"]


def escape_and_bold_keywords(text: str) -> str:
    """Applies bolding to identified keywords and escapes HTML in between."""
    temp_text = escape(text)

    # Sort patterns by length descending to match longer phrases first
    # This prevents e.g. "HP" from being bolded before "HP Pavilion"
    all_patterns = sorted(BRANDS + PRODUCT_NAME_COMPONENTS + TECH_SPECS_PATTERNS + SOFTWARE_GAMES, key=len, reverse=True)

    for pattern in all_patterns:
        # Use re.escape() for patterns that are literal strings to treat special chars literally
        # Use \b for word boundaries where appropriate
        if any(kw in pattern for kw in BRANDS + PRODUCT_NAME_COMPONENTS + SOFTWARE_GAMES): # These are usually whole words/phrases
            temp_text = re.sub(r'\b' + re.escape(pattern) + r'\b', r'<strong>\g<0></strong>', temp_text, flags=re.IGNORECASE)
        else: # For tech specs patterns that might be more flexible or contain regex directly
            temp_text = re.sub(pattern, r'<strong>\g<0></strong>', temp_text, flags=re.IGNORECASE)

    return temp_text


def auto_format_description_with_nlp(raw_text: str, product_name: str) -> str:
    """
    Formats raw product description text into structured HTML using rule-based logic.

    Args:
        raw_text: The unformatted text description.
        product_name: The name of the product to use as the main heading.

    Returns:
        A string containing the HTML formatted description.
    """
    if not raw_text:
        return ""

    normalized_text = normalizer.normalize(raw_text)
    cleaned_text = normalized_text.replace('¶', '\n\n') # Replace the custom paragraph marker from your data.

    blocks = re.split(r'\n{2,}', cleaned_text) # Split by two or more newlines for major blocks
    
    formatted_html_parts = []
    
    # Add the main product name as H2 (escaped for safety)
    formatted_html_parts.append(f'<h2 style="text-align: center;">{escape(product_name)}</h2>\n')

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Rule 1: Identify "Return Policy" or "Warranty" type blocks
        # These blocks often contain repetitive phrases related to returns/replacements/warranty
        if any(kw in block for kw in ["بازگشت", "بازپرداخت", "جایگزینی", "گارانتی", "قابل بازگشت", "شرایط اصلی"]):
            lines_in_block = block.split('\n')
            list_content = []
            
            for line in lines_in_block:
                line = line.strip()
                if not line:
                    continue 

                # If line starts with a bullet/number or contains specific keywords
                if re.match(r'^(?:[-•*]|\d+\.)\s*', line) or \
                   any(kw in line for kw in ["برچسب های MRP", "کتابچه راهنمای کاربر", "کارتهای گارانتی", "لوازم جانبی", "جعبه بیرونی", "بسته بندی سازنده"]):
                    list_content.append(f"<li>{escape_and_bold_keywords(line)}</li>")
                else: # Treat as a regular sentence within this policy block, perhaps needing <br>
                    # If this is not the first item, and it's not a list, maybe it should be a new paragraph
                    if list_content and not formatted_html_parts[-1].startswith('<p'):
                         # This logic needs refinement. For simplicity, let's just make it a single paragraph if it's not a list.
                         # Or, put it as a <br> separated within the policy block.
                        if formatted_html_parts and formatted_html_parts[-1].startswith('<p'):
                             formatted_html_parts[-1] = mark_safe(formatted_html_parts[-1].replace('</p>', f'<br>{escape_and_bold_keywords(line)}</p>'))
                        else:
                             formatted_html_parts.append(f'<p style="text-align: justify;">{escape_and_bold_keywords(line)}</p>')
                    else:
                        formatted_html_parts.append(f'<p style="text-align: justify;">{escape_and_bold_keywords(line)}</p>')
            
            if list_content:
                formatted_html_parts.append("<ul>" + "\n".join(list_content) + "</ul>")
            continue # Move to next main block

        # Rule 2: Identify blocks that are essentially lists of model names/references
        is_model_list_block = False
        lines_in_block = block.split('\n')
        if len(lines_in_block) > 3: # Only consider if it has multiple lines
            model_list_lines_count = 0
            for line in lines_in_block:
                line = line.strip()
                # Check for product names/brands and common specs in each line
                if (re.search(r'(?:' + '|'.join(BRANDS) + r')', line, re.IGNORECASE) or \
                    re.search(r'(?:' + '|'.join(PRODUCT_NAME_COMPONENTS) + r')', line, re.IGNORECASE) or \
                    re.search(r'SSD|RAM|HDD|Core\s*i\d+|Ryzen\s*\d+', line, re.IGNORECASE)) \
                    and len(line.split()) < 25: # Heuristic: line is short and contains product info
                    model_list_lines_count += 1
            if model_list_lines_count / len(lines_in_block) > 0.6: # If more than 60% of lines are potential model names
                is_model_list_block = True

        if is_model_list_block:
            list_content = []
            for line in lines_in_block:
                line = line.strip()
                if line:
                    list_content.append(f"<li>{escape_and_bold_keywords(line)}</li>")
            if list_content:
                formatted_html_parts.append("<ul>" + "\n".join(list_content) + "</ul>")
            continue # Move to next main block

        # Rule 3: For regular descriptive paragraphs
        sentences = hazm.sent_tokenize(block)
        current_paragraph_buffer = []

        for sentence in sentences:
            sentence_text = sentence.strip()
            if not sentence_text:
                continue

            # Heuristic for Headings (h3, h4) within descriptive blocks
            is_heading_candidate = False
            for keyword in HEADING_KEYWORDS:
                if (keyword.lower() in sentence_text.lower() and len(sentence_text.split()) < 15) or \
                   (len(sentence_text.split()) < 7 and sentence_text.endswith(':')): # e.g., "پردازنده:"
                    
                    if current_paragraph_buffer: # Flush any accumulated paragraph sentences
                        formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_buffer)}</p>')
                        current_paragraph_buffer = []

                    # Determine heading level
                    if len(sentence_text.split()) < 6 or (sentence_text.endswith(':') and len(sentence_text.split()) < 5):
                        formatted_html_parts.append(f'<h4 style="text-align: center;">{escape_and_bold_keywords(sentence_text)}</h4>')
                    else:
                        formatted_html_parts.append(f'<h3 style="text-align: center;">{escape_and_bold_keywords(sentence_text)}</h3>')
                    is_heading_candidate = True
                    break
            
            if is_heading_candidate:
                continue # Skip to next sentence, as this one was a heading

            # Apply general formatting (bolding, coloring) to the sentence
            formatted_sentence = escape_and_bold_keywords(sentence_text)
            
            # Apply color to "Pros" and "Cons" keywords
            for pro_kw in PROS_KEYWORDS:
                formatted_sentence = re.sub(r'\b' + re.escape(pro_kw) + r'\b', f'<span style="color: green;">{pro_kw}</span>', formatted_sentence, flags=re.IGNORECASE)
            for con_kw in CONS_KEYWORDS:
                formatted_sentence = re.sub(r'\b' + re.escape(con_kw) + r'\b', f'<span style="color: red;">{con_kw}</span>', formatted_sentence, flags=re.IGNORECASE)
            
            # Add to paragraph buffer
            current_paragraph_buffer.append(formatted_sentence)
        
        # After processing all sentences in a descriptive block, finalize the paragraph
        if current_paragraph_buffer:
            formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_buffer)}</p>')

    # Final HTML string
    final_html = "\n".join(formatted_html_parts)

    return mark_safe(final_html)


class Command(BaseCommand):
    help = 'Formats existing product descriptions to HTML using NLP rules.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting bulk description formatting...'))

        # Fetch products that have descriptions and have not been formatted (or assume all need formatting)
        products_to_process = Product.objects.filter(description__isnull=False).exclude(description='').iterator()
        
        updated_count = 0
        total_products = Product.objects.filter(description__isnull=False).exclude(description='').count()

        for i, product in enumerate(products_to_process):
            self.stdout.write(self.style.NOTICE(f'Processing product {i+1}/{total_products}: {product.product_name}'))
            
            original_description = product.description
            
            # Heuristic to skip already formatted descriptions
            # If the description contains common HTML tags we add, assume it's already processed.
            if "<p style=" in original_description and "<strong>" in original_description:
                self.stdout.write(self.style.WARNING(f'  Skipping: Description for "{product.product_name}" seems already formatted.'))
                continue

            try:
                formatted_description = auto_format_description_with_nlp(original_description, product.product_name)
                
                # Only save if there's an actual change
                if original_description != formatted_description:
                    product.description = formatted_description
                    product.save(update_fields=['description']) # Save only the description field to be efficient
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  Successfully formatted "{product.product_name}".'))
                else:
                    self.stdout.write(self.style.NOTICE(f'  No significant changes needed for "{product.product_name}".'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error formatting "{product.product_name}": {e}'))
                # You might want to log this error to a file or database for later review.

        self.stdout.write(self.style.SUCCESS(f'Finished formatting. Total updated: {updated_count} out of {total_products} products with descriptions.'))