# myapp/management/commands/format_single_description.py
import re
import hazm
from django.core.management.base import BaseCommand
from django.utils.html import escape, mark_safe
from apps.products.models import Product # Adjust 'myapp' to your actual app name
# --- Hazm Component Initialization (Load once for efficiency) ---
try:
    normalizer = hazm.Normalizer()
    # In newer Hazm versions (like 0.10.0), POSTagger and NamedEntityRecognizer
    # might need to be imported differently or initialized without a model argument
    # if they rely on pre-downloaded NLTK data by Hazm's utils.
    
    # Try initializing without model path, assuming default models/resources are used by Hazm internally.
    # If this still fails, it means the structure of hazm.POSTagger and hazm.NamedEntityRecognizer
    # or their availability has changed significantly, or data is missing.
    pos_tagger = hazm.POSTagger() 
    ner = hazm.NamedEntityRecognizer()
    
    print("Hazm models loaded successfully.")
except Exception as e:
    # A more specific error handling:
    if "No such file or directory" in str(e) or "missing resource" in str(e):
        print(f"Error: Hazm models are missing. Please download them first by running:")
        print(f"    python -c \"import hazm; hazm.utils.download_model('all')\"")
    else:
        print(f"Error loading Hazm components: {e}") # Catches the original attribute error or other issues.
    exit(1) # Exit with an error code if critical components fail to load.


# --- Define Global Rule Sets (Lists of keywords and patterns) ---
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

    all_patterns = sorted(BRANDS + PRODUCT_NAME_COMPONENTS + TECH_SPECS_PATTERNS + SOFTWARE_GAMES, key=len, reverse=True)

    for pattern in all_patterns:
        if any(kw in pattern for kw in BRANDS + PRODUCT_NAME_COMPONENTS + SOFTWARE_GAMES):
            temp_text = re.sub(r'\b' + re.escape(pattern) + r'\b', r'<strong>\g<0></strong>', temp_text, flags=re.IGNORECASE)
        else: 
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
    cleaned_text = normalized_text.replace('¶', '\n\n')

    blocks = re.split(r'\n{2,}', cleaned_text)
    
    formatted_html_parts = []
    
    formatted_html_parts.append(f'<h2 style="text-align: center;">{escape(product_name)}</h2>\n')

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Rule 1: Identify "Return Policy" or "Warranty" type blocks
        if any(kw in block for kw in ["بازگشت", "بازپرداخت", "جایگزینی", "گارانتی", "قابل بازگشت", "شرایط اصلی"]):
            lines_in_block = block.split('\n')
            list_content = []
            current_paragraph_lines = []
            
            for line in lines_in_block:
                line = line.strip()
                if not line:
                    continue 

                if re.match(r'^(?:[-•*]|\d+\.)\s*', line) or \
                   any(kw in line for kw in ["برچسب های MRP", "کتابچه راهنمای کاربر", "کارتهای گارانتی", "لوازم جانبی", "جعبه بیرونی", "بسته بندی سازنده"]):
                    if current_paragraph_lines:
                        formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_lines)}</p>')
                        current_paragraph_lines = []
                    list_content.append(f"<li>{escape_and_bold_keywords(line)}</li>")
                else:
                    if list_content:
                        formatted_html_parts.append("<ul>" + "\n".join(list_content) + "</ul>")
                        list_content = []
                    current_paragraph_lines.append(escape_and_bold_keywords(line))
            
            if list_content:
                formatted_html_parts.append("<ul>" + "\n".join(list_content) + "</ul>")
            if current_paragraph_lines:
                formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_lines)}</p>')
            continue

        # Rule 2: Identify blocks that are essentially lists of model names/references
        is_model_list_block = False
        lines_in_block = block.split('\n')
        if len(lines_in_block) > 3:
            model_list_lines_count = 0
            for line in lines_in_block:
                line = line.strip()
                if (re.search(r'(?:' + '|'.join(BRANDS) + r')', line, re.IGNORECASE) or \
                    re.search(r'(?:' + '|'.join(PRODUCT_NAME_COMPONENTS) + r')', line, re.IGNORECASE) or \
                    re.search(r'SSD|RAM|HDD|Core\s*i\d+|Ryzen\s*\d+', line, re.IGNORECASE)) \
                    and len(line.split()) < 25:
                    model_list_lines_count += 1
            if model_list_lines_count / len(lines_in_block) > 0.6:
                is_model_list_block = True

        if is_model_list_block:
            list_content = []
            for line in lines_in_block:
                line = line.strip()
                if line:
                    list_content.append(f"<li>{escape_and_bold_keywords(line)}</li>")
            if list_content:
                formatted_html_parts.append("<ul>" + "\n".join(list_content) + "</ul>")
            continue

        # Rule 3: For regular descriptive paragraphs
        sentences = hazm.sent_tokenize(block)
        current_paragraph_buffer = []

        for sentence in sentences:
            sentence_text = sentence.strip()
            if not sentence_text:
                continue

            is_heading_candidate = False
            for keyword in HEADING_KEYWORDS:
                if (keyword.lower() in sentence_text.lower() and len(sentence_text.split()) < 15) or \
                   (len(sentence_text.split()) < 7 and sentence_text.endswith(':')):
                    
                    if current_paragraph_buffer:
                        formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_buffer)}</p>')
                        current_paragraph_buffer = []

                    if len(sentence_text.split()) < 6 or (sentence_text.endswith(':') and len(sentence_text.split()) < 5):
                        formatted_html_parts.append(f'<h4 style="text-align: center;">{escape_and_bold_keywords(sentence_text)}</h4>')
                    else:
                        formatted_html_parts.append(f'<h3 style="text-align: center;">{escape_and_bold_keywords(sentence_text)}</h3>')
                    is_heading_candidate = True
                    break
            
            if is_heading_candidate:
                continue

            formatted_sentence = escape_and_bold_keywords(sentence_text)
            
            for pro_kw in PROS_KEYWORDS:
                formatted_sentence = re.sub(r'\b' + re.escape(pro_kw) + r'\b', f'<span style="color: green;">{pro_kw}</span>', formatted_sentence, flags=re.IGNORECASE)
            for con_kw in CONS_KEYWORDS:
                formatted_sentence = re.sub(r'\b' + re.escape(con_kw) + r'\b', f'<span style="color: red;">{con_kw}</span>', formatted_sentence, flags=re.IGNORECASE)
            
            current_paragraph_buffer.append(formatted_sentence)
        
        if current_paragraph_buffer:
            formatted_html_parts.append(f'<p style="text-align: justify;">{" ".join(current_paragraph_buffer)}</p>')

    final_html = "\n".join(formatted_html_parts)

    return mark_safe(final_html)


class Command(BaseCommand):
    help = 'Formats a single product description by ID using NLP rules.'

    def add_arguments(self, parser):
        parser.add_argument('product_id', type=int, help='The ID of the product to format.')

    def handle(self, *args, **kwargs):
        product_id = kwargs['product_id']
        self.stdout.write(self.style.SUCCESS(f'Attempting to format description for product with ID: {product_id}'))

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Product with ID {product_id} does not exist.'))
            return

        if not product.description:
            self.stdout.write(self.style.WARNING(f'Product with ID {product_id} has no description to format.'))
            return

        original_description = product.description
        
        # Heuristic to skip already formatted descriptions for safety, especially if you modify them manually.
        if "<p style=" in original_description and "<strong>" in original_description:
            self.stdout.write(self.style.WARNING(f'Description for product ID {product_id} seems already formatted. Skipping.'))
            # You might offer an option to force re-format if needed in a real scenario
            return

        try:
            formatted_description = auto_format_description_with_nlp(original_description, product.product_name)
            
            if original_description != formatted_description:
                product.description = formatted_description
                product.save(update_fields=['description']) # Save only the description field for efficiency
                self.stdout.write(self.style.SUCCESS(f'Successfully formatted description for product ID {product_id} ("{product.product_name}").'))
            else:
                self.stdout.write(self.style.NOTICE(f'No changes needed for product ID {product_id} ("{product.product_name}").'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error formatting description for product ID {product_id} ("{product.product_name}"): {e}'))
            # Log this error for debugging.