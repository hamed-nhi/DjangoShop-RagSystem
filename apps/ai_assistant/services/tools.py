# apps/ai_assistant/services/tools.py

from typing import List
from langchain_core.tools import tool
from apps.products.models import Product
from apps.orders.shop_card import ShopCart
from . import hybrid_retriever
from middlewares.middlewares import RequestMiddleware
from typing import List, Optional
from .global_services import hybrid_retriever
import locale

try:
    locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

@tool
def search_products(
    query: str, 
    price_min: Optional[int] = None, 
    price_max: Optional[int] = None, 
    price_around: Optional[int] = None
) -> str:
    """
    Searches for products based on text and optional price filters.
    - query: The user's search text (e.g., 'Asus gaming laptop').
    - price_min: Use for explicit lower bounds like 'from 100 million'.
    - price_max: Use for explicit upper bounds like 'under 150 million'.
    - price_around: Use ONLY for ambiguous ranges like 'around 150 million'.
    """
    print(f"--- Search tool invoked with: query='{query}', min={price_min}, max={price_max}, around={price_around} ---")

    # --- New, Smarter Logic ---
    # If the user gives an upper limit but no lower limit, create a reasonable lower limit.
    if price_max and not price_min and not price_around:
        # Assume the user wants products in the top 30% of their budget range.
        price_min = int(price_max * 0.85) 
        print(f"   -> 'price_max' without 'price_min' detected. Calculated new range: {price_min}-{price_max}")

    # Logic for 'price_around' remains the same
    elif price_around and not price_min and not price_max:
        range_percent = 0.20  # +/- 20% range
        price_min = int(price_around * (1 - range_percent))
        price_max = int(price_around * (1 + range_percent))
        print(f"   -> 'price_around' detected. Calculated new range: {price_min}-{price_max}")

    # Build the filter string for MeiliSearch
    filters = []
    if price_min is not None:
        filters.append(f"price >= {price_min}")
    if price_max is not None:
        filters.append(f"price <= {price_max}")
    meili_filter = " AND ".join(filters) if filters else None

    try:
        product_ids = hybrid_retriever.search(query, k=10, filters=meili_filter)
        if not product_ids:
            return "Unfortunately, no products were found with these specifications."
            
        products_query = Product.objects.filter(id__in=product_ids)

        # Final, strict price filtering
        if price_min is not None:
            products_query = products_query.filter(price__gte=price_min)
        if price_max is not None:
            products_query = products_query.filter(price__lte=price_max)

        # Sort the final results by price descending to show the best options first
        final_products = list(products_query.order_by('-price')[:5])
        
        if not final_products:
             return "Unfortunately, no products were found with these specifications in the specified price range."

        results = ["Here are the best matches found in your specified price range:\n"]
        for p in final_products:
            results.append(f"- Name: {p.product_name} (ID: {p.id})\n  Price: {p.price} تومان")
        return "\n".join(results)
    except Exception as e:
        return f"An error occurred while searching for products: {e}"

@tool
def compare_products(product_ids: List[int]) -> str:
    """زمانی از این ابزار استفاده کن که کاربر صراحتاً درخواست مقایسه دو یا چند محصول را دارد."""
    print(f"--- ابزار مقایسه فراخوانی شد برای محصولات: {product_ids} ---")
    if not product_ids or len(product_ids) < 2:
        return "برای مقایسه حداقل به دو شناسه محصول نیاز است."
    try:
        products = Product.objects.filter(id__in=product_ids).prefetch_related('product_features__feature')
        if products.count() != len(product_ids):
            return "یک یا چند محصول با شناسه‌های داده شده یافت نشد."
        all_features = set()
        product_data = {}
        for p in products:
            features = {pf.feature.feature_name: pf.value for pf in p.product_features.all()}
            product_data[p.id] = {'name': p.product_name, 'features': features}
            all_features.update(features.keys())
        header = "| ویژگی | " + " | ".join([p.product_name[:20] for p in products]) + " |"
        separator = "|---|" * (len(products) + 1)
        rows = [header, separator]
        for feature in sorted(list(all_features)):
            row = f"| {feature} |"
            for p in products:
                value = product_data[p.id]['features'].get(feature, '---')
                row += f" {value} |"
            rows.append(row)
        return "جدول مقایسه محصولات:\n" + "\n".join(rows)
    except Exception as e:
        return f"هنگام مقایسه محصولات خطایی رخ داد: {e}"

@tool
def add_to_cart(product_id: int) -> str:
    """زمانی از این ابزار استفاده کن که کاربر قصد خرید دارد و می‌خواهد محصولی را به سبد خرید اضافه کند."""
    print(f"--- ابزار افزودن به سبد خرید فراخوانی شد برای محصول: {product_id} ---")
    try:
        request = RequestMiddleware(get_response=None).thread_local.current_request
        if not request:
            return "خطای سیستمی: امکان دسترسی به سبد خرید وجود ندارد."
        product = Product.objects.get(id=product_id)
        cart = ShopCart(request)
        cart.add(product, 1)
        return f"محصول '{product.product_name}' با موفقیت به سبد خرید شما اضافه شد."
    except Product.DoesNotExist:
        return f"محصولی با شناسه {product_id} یافت نشد."
    except Exception as e:
        return f"هنگام افزودن محصول به سبد خرید خطایی رخ داد: {e}"